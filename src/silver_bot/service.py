from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from zoneinfo import ZoneInfo
from .sources import fetch
from .aggregation import aggregate

PERSIAN_DIGITS = str.maketrans("0123456789.", "۰۱۲۳۴۵۶۷۸۹٫")
SOURCE_NAMES = {"digikala": "دیجی‌کالا", "noghresea": "نقره‌سی", "tokeniko": "توکنیکو", "melligold": "ملی‌گلد"}

def _number(value, places=0):
    return f"{value:,.{places}f}".replace(",", "٬").translate(PERSIAN_DIGITS)

def format_message(average, observations, config, previous=None):
    local = datetime.now(timezone.utc).astimezone(ZoneInfo(config.timezone)); lines = ["🥈 قیمت نقره ۹۹۹", "", f"💰 {_number(average)} تومان / گرم"]
    change = (average - previous) / previous * Decimal("100") if previous and previous > 0 else Decimal(0)
    icon = "🟢" if change > 0 else "🔴" if change < 0 else "🟡"
    lines += [f"{icon} {change:+.2f}%"]
    lines += [""]
    if config.breakdown:
        lines += ["📊 جزئیات منابع"] + [f"• {SOURCE_NAMES.get(o.source, o.source)}: {_number(o.price)} تومان" for o in observations if o.price is not None and not o.excluded] + [""]
    lines += [f"✅ منابع معتبر: {sum(o.price is not None and not o.excluded for o in observations)} از {len(observations)}", f"🕒 بروزرسانی: {local:%Y/%m/%d - %H:%M}"]
    return "\n".join(lines)

def cycle(config, database, bale=None, publish=True):
    cycle_id = str(uuid4()); observations = [fetch(s, config.multipliers[s], config.fields.get(s,""), config.read_timeout, config.retries) for s in config.enabled if config.enabled[s]]
    average, valid = aggregate(observations, config.weights, config.min_sources, config.min_price, config.max_price, config.max_deviation)
    previous = database.latest_average()
    status = "success" if average is not None else "insufficient_sources"; database.run(cycle_id, observations, average, status, config.weights)
    if average is None: return None
    if bale and publish: bale.send(config.channel, format_message(average, valid, config, previous))
    return average
