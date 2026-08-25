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

def format_message(average, observations, config, previous=None, usdt_price=None, xag_price=None, premium=None):
    local = datetime.now(timezone.utc).astimezone(ZoneInfo(config.timezone)); lines = ["🥈 قیمت نقره ۹۹۹", "", f"💰 {_number(average)} تومان / گرم"]
    change = (average - previous) / previous * Decimal("100") if previous and previous > 0 else Decimal(0)
    icon = "🟢" if change > 0 else "🔴" if change < 0 else "🟡"
    lines += [f"{icon} {change:+.2f}%"]
    if usdt_price is not None: lines += [f"💵 دلار (USDT): {_number(usdt_price)} تومان"]
    if xag_price is not None: lines += [f"🌍 XAG: ${xag_price:.2f} / oz"]
    if premium:
        lines += [f"📊 حباب میانگین وزنی: {_signed(premium['weighted_absolute'])} تومان ({_signed(premium['weighted_percent'], 2)}%)"]
    lines += [""]
    if config.breakdown:
        percentages = {item["source"]: item["percent"] for item in premium["items"]} if premium else {}
        lines += ["📊 جزئیات منابع"] + [f"• {SOURCE_NAMES.get(o.source, o.source)}: {_signed(percentages[o.source], 2)}% | {_number(o.price)} تومان" if o.source in percentages else f"• {SOURCE_NAMES.get(o.source, o.source)}: {_number(o.price)} تومان" for o in observations if o.price is not None and not o.excluded] + [""]
    lines += [f"✅ منابع معتبر: {sum(o.price is not None and not o.excluded for o in observations)} از {len(observations)}", f"🕒 بروزرسانی: {local:%Y/%m/%d - %H:%M}"]
    return "\n".join(lines)

def cycle(config, database, bale=None, publish=True):
    cycle_id = str(uuid4()); observations = [fetch(s, config.multipliers[s], config.fields.get(s,""), config.read_timeout, config.retries) for s in config.enabled if config.enabled[s]]
    average, valid = aggregate(observations, config.weights, config.min_sources, config.min_price, config.max_price, config.max_deviation)
    previous = database.latest_average()
    usdt_price = fetch_usdt(config.fields["abantether"], config.read_timeout, config.retries)
    xag_price = fetch_xag(config.read_timeout, config.retries)
    global_price = xag_price * usdt_price / TROY_OUNCE_GRAMS if xag_price and usdt_price and usdt_price > 0 else None
    premium = calculate_premiums(valid, global_price, config.weights)
    status = "success" if average is not None else "insufficient_sources"; database.run(cycle_id, observations, average, status, config.weights, xag_price, usdt_price, premium)
    if average is None: return None
    if bale and publish: bale.send(config.channel, format_message(average, valid, config, previous, usdt_price, xag_price, premium))
    return average
