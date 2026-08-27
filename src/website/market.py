from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.db import connection

SOURCE_NAMES = {"digikala": "دیجی‌کالا", "noghresea": "نقره‌سی", "tokeniko": "توکنیکو", "melligold": "ملی‌گلد"}
RANGES = {"24h": (timedelta(hours=24), 600), "7d": (timedelta(days=7), 3600), "30d": (timedelta(days=30), 14400), "90d": (timedelta(days=90), 43200), "1y": (timedelta(days=365), 86400)}


def _decimal(value):
    try:
        return Decimal(str(value)) if value is not None else None
    except (InvalidOperation, ValueError):
        return None


def _price(value):
    value = _decimal(value)
    return int(value.quantize(Decimal("1"))) if value is not None else None


def _percent(value):
    value = _decimal(value)
    return float(value.quantize(Decimal("0.01"))) if value is not None else None


def _iso(value):
    return value.replace("+00:00", "Z") if value else None


def _parse_time(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _row_dict(row, columns):
    return dict(zip(columns, row))


def latest_run():
    columns = ("cycle_id", "finished_at", "weighted_average_toman", "xag_usd_per_oz", "usdt_toman_per_usd", "global_price_toman", "weighted_premium_toman", "weighted_premium_percent", "valid_source_count", "candidate_source_count")
    with connection.cursor() as cursor:
        cursor.execute("SELECT cycle_id, finished_at, weighted_average_toman, xag_usd_per_oz, usdt_toman_per_usd, global_price_toman, weighted_premium_toman, weighted_premium_percent, valid_source_count, candidate_source_count FROM aggregation_runs WHERE status='success' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
    if not row:
        return None
    data = _row_dict(row, columns)
    data["updated_at"] = _iso(data.pop("finished_at"))
    data["reference_price_toman"] = _price(data.pop("weighted_average_toman"))
    xag = data.pop("xag_usd_per_oz")
    data["xag_usd"] = float(_decimal(xag)) if xag is not None else None
    data["usdt_toman"] = _price(data.pop("usdt_toman_per_usd"))
    data["global_value_toman"] = _price(data.pop("global_price_toman"))
    data["premium_toman"] = _price(data.pop("weighted_premium_toman"))
    data["premium_pct"] = _percent(data.pop("weighted_premium_percent"))
    data["valid_sources"] = data.pop("valid_source_count") or 0
    data.pop("candidate_source_count")
    data["total_sources"] = len(SOURCE_NAMES)
    return data


def freshness(updated_at):
    timestamp = _parse_time(updated_at)
    if not timestamp:
        return {"state": "no_data", "label": "اطلاعاتی ثبت نشده است", "age_seconds": None}
    age = max(0, int((datetime.now(timezone.utc) - timestamp).total_seconds()))
    stale = age > settings.STALE_AFTER_SECONDS
    minutes = age // 60
    label = "چند لحظه پیش" if age < 90 else f"{minutes} دقیقه پیش"
    return {"state": "stale" if stale else "fresh", "label": label, "age_seconds": age}


def latest_sources():
    run = latest_run()
    if not run:
        return []
    with connection.cursor() as cursor:
        cursor.execute("SELECT source, normalized_price_toman, valid, excluded_reason FROM source_observations WHERE cycle_id=%s ORDER BY id", [run["cycle_id"]])
        rows = cursor.fetchall()
    return [{"source": source, "name": SOURCE_NAMES.get(source, source), "price_toman": _price(price), "available": bool(valid), "reason": reason or None} for source, price, valid, reason in rows]


def _point_change(hours):
    now = datetime.now(timezone.utc)
    cutoff = (now - timedelta(hours=hours)).isoformat()
    with connection.cursor() as cursor:
        cursor.execute("SELECT weighted_average_toman FROM aggregation_runs WHERE status='success' AND finished_at <= %s ORDER BY finished_at DESC LIMIT 1", [cutoff])
        row = cursor.fetchone()
    return _decimal(row[0]) if row else None


def summary():
    current = latest_run()
    if not current:
        return {"trend": None, "change_24h_pct": None, "change_7d_pct": None, "high_24h": None, "low_24h": None}
    previous_24 = _point_change(24)
    previous_7 = _point_change(24 * 7)
    current_price = _decimal(current["reference_price_toman"])
    change_24 = (current_price - previous_24) / previous_24 * 100 if current_price and previous_24 else None
    change_7 = (current_price - previous_7) / previous_7 * 100 if current_price and previous_7 else None
    if change_7 is None:
        trend = None
    elif change_7 >= 3:
        trend = {"direction": "up", "label": "صعودی", "description": "روند هفت‌روزه صعودی است."}
    elif change_7 >= 1:
        trend = {"direction": "up", "label": "صعودی ملایم", "description": "روند هفت‌روزه افزایش ملایمی دارد."}
    elif change_7 <= -3:
        trend = {"direction": "down", "label": "نزولی", "description": "روند هفت‌روزه نزولی است."}
    elif change_7 <= -1:
        trend = {"direction": "down", "label": "نزولی ملایم", "description": "روند هفت‌روزه کاهش ملایمی دارد."}
    else:
        trend = {"direction": "flat", "label": "خنثی", "description": "روند هفت‌روزه تقریباً خنثی است."}
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    with connection.cursor() as cursor:
        cursor.execute("SELECT MIN(weighted_average_toman), MAX(weighted_average_toman) FROM aggregation_runs WHERE status='success' AND finished_at >= %s", [cutoff])
        high_low = cursor.fetchone()
    return {"change_24h_pct": _percent(change_24), "change_7d_pct": _percent(change_7), "high_24h": _price(high_low[1]), "low_24h": _price(high_low[0]), "trend": trend}


def market_latest():
    current = latest_run()
    if not current:
        return {"data": None, "freshness": freshness(None)}
    current.update(summary())
    current["freshness"] = freshness(current["updated_at"])
    return {"data": current, "freshness": current["freshness"]}


def history(range_name):
    duration, bucket_seconds = RANGES[range_name]
    cutoff = (datetime.now(timezone.utc) - duration).isoformat()
    with connection.cursor() as cursor:
        cursor.execute("SELECT finished_at, weighted_average_toman, global_price_toman, weighted_premium_percent FROM aggregation_runs WHERE status='success' AND finished_at >= %s ORDER BY finished_at", [cutoff])
        rows = cursor.fetchall()
    points = {}
    for finished_at, reference, global_value, premium in rows:
        timestamp = _parse_time(finished_at)
        if not timestamp:
            continue
        bucket = int(timestamp.timestamp() // bucket_seconds)
        points[bucket] = {"timestamp": _iso(finished_at), "reference_price_toman": _price(reference), "global_value_toman": _price(global_value), "premium_pct": _percent(premium)}
    return list(points.values())
