from decimal import Decimal
from statistics import median

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
