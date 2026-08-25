from decimal import Decimal
from statistics import median

TROY_OUNCE_GRAMS = Decimal("31.1034768")

def aggregate(observations, weights, minimum, low, high, max_deviation):
    candidates = [o for o in observations if o.price is not None and low <= o.price <= high and weights[o.source] > 0]
    for o in observations:
        if o.price is not None and not (low <= o.price <= high): o.excluded = "outside_range"
    if len(candidates) >= 3:
        med = Decimal(str(median([o.price for o in candidates])))
        for o in candidates[:]:
            if med and abs(o.price-med) / med * 100 > max_deviation: o.excluded = "deviation_from_median"; candidates.remove(o)
    total = sum((weights[o.source] for o in candidates), Decimal(0))
    if len(candidates) < minimum or not total: return None, candidates
    return sum((o.price * weights[o.source] for o in candidates), Decimal(0)) / total, candidates

def calculate_premiums(observations, global_price, weights):
    if global_price is None or global_price <= 0: return None
    candidates = [o for o in observations if o.price is not None and not o.excluded and weights[o.source] > 0]
    total = sum((weights[o.source] for o in candidates), Decimal(0))
    if not candidates or not total: return None
    items = [{"source": o.source, "absolute": o.price - global_price, "percent": (o.price - global_price) / global_price * 100} for o in candidates]
    weighted = sum((item["absolute"] * weights[item["source"]] for item in items), Decimal(0)) / total
    return {"global": global_price, "items": items, "weighted_absolute": weighted, "weighted_percent": weighted / global_price * 100}
