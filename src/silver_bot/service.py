from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from zoneinfo import ZoneInfo
from .sources import fetch, fetch_usdt, fetch_xag
from .aggregation import aggregate, calculate_premiums, TROY_OUNCE_GRAMS

PERSIAN_DIGITS = str.maketrans("0123456789.", "۰۱۲۳۴۵۶۷۸۹٫")
SOURCE_NAMES = {"digikala": "دیجی‌کالا", "noghresea": "نقره‌سی", "tokeniko": "توکنیکو", "melligold": "ملی‌گلد"}

def _number(value, places=0):
    return f"{value:,.{places}f}".replace(",", "٬").translate(PERSIAN_DIGITS)

def _signed(value, places=0):
    return ("+" if value >= 0 else "-") + _number(abs(value), places)

def _percentage(value):
    return f"\u2066{_signed(value, 2)}٪\u2069"

def should_publish(config, average, last_published, now=None):
    if not config.send_enabled: return False
    if last_published is None: return True
    previous, published_at = last_published
    now = now or datetime.now(timezone.utc)
    if (now - published_at).total_seconds() >= config.send_interval: return True
    return previous <= 0 or abs(average - previous) / previous * Decimal("100") > config.send_threshold_percent

def format_message(average, observations, config, previous=None, usdt_price=None, xag_price=None, premium=None):
    local = datetime.now(timezone.utc).astimezone(ZoneInfo(config.timezone)); lines = ["🥈 نقره ۹۹۹ — تومان/گرم", "", f"💰 قیمت لحظه: {_number(average)}"]
    change = (average - previous) / previous * Decimal("100") if previous and previous > 0 else Decimal(0)
    icon = "🟢" if change > 0 else "🔴" if change < 0 else "🟡"
    lines += [f"{icon} درصد تغییرات: {_percentage(change)}"]
    if premium:
        lines += [f"📊 حباب میانگین وزنی: {_signed(premium['weighted_absolute'])} تومان ({_percentage(premium['weighted_percent'])})"]
    lines += [""]
    if usdt_price is not None or xag_price is not None:
        lines += ["🌐 بازار جهانی"]
        if usdt_price is not None: lines += [f"💵 دلار (USDT): {_number(usdt_price)} تومان"]
        if xag_price is not None: lines += [f"🌍 انس جهانی نقره: ${xag_price:.2f}"]
        lines += [""]
    if config.breakdown:
        percentages = {item["source"]: item["percent"] for item in premium["items"]} if premium else {}
        lines += ["📊 بازار ایران"] + [f"• {SOURCE_NAMES.get(o.source, o.source)}: {_percentage(percentages[o.source])} | {_number(o.price)}" if o.source in percentages else f"• {SOURCE_NAMES.get(o.source, o.source)}: {_number(o.price)}" for o in observations if o.price is not None and not o.excluded] + [""]
    lines += [f"✅ {_number(sum(o.price is not None and not o.excluded for o in observations))} از {_number(len(observations))} منبع معتبر", f"🕒 {local:%Y/%m/%d — %H:%M}"]
    if channel := getattr(config, "channel", ""):
        lines += [f"\u2066{channel}\u2069"]
    return "\n".join(lines)

def cycle(config, database, bale=None, publish=True):
    cycle_id = str(uuid4()); observations = [fetch(s, config.multipliers[s], config.fields.get(s,""), config.read_timeout, config.retries) for s in config.enabled if config.enabled[s]]
    average, valid = aggregate(observations, config.weights, config.min_sources, config.min_price, config.max_price, config.max_deviation)
    last_published = database.latest_published(); previous = last_published[0] if last_published else None
    usdt_price = fetch_usdt(config.fields["abantether"], config.read_timeout, config.retries)
    xag_price = fetch_xag(config.read_timeout, config.retries)
    global_price = xag_price * usdt_price / TROY_OUNCE_GRAMS if xag_price and usdt_price and usdt_price > 0 else None
    premium = calculate_premiums(valid, global_price, config.weights)
    status = "success" if average is not None else "insufficient_sources"; database.run(cycle_id, observations, average, status, config.weights, xag_price, usdt_price, premium)
    if average is None: return None
    if bale and publish and should_publish(config, average, last_published):
        result = bale.send(config.channel, format_message(average, valid, config, previous, usdt_price, xag_price, premium))
        database.mark_published(cycle_id, result.get("message_id") if isinstance(result, dict) else None)
    return average
