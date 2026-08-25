from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4
from zoneinfo import ZoneInfo
from .sources import fetch
from .aggregation import aggregate

def format_message(average, observations, config):
    value = f"{average:,.0f}".replace(",", "٬"); local = datetime.now(timezone.utc).astimezone(ZoneInfo(config.timezone)); lines = ["🥈 قیمت میانگین نقره ۹۹۹", "", f"{value} تومان / گرم", ""]
    if config.breakdown:
        lines += [f"{o.source}: {o.price:,.0f}".replace(",", "٬") for o in observations if o.price is not None and not o.excluded] + [""]
    lines += [f"منابع معتبر: {sum(o.price is not None and not o.excluded for o in observations)}/{len(observations)}", f"آخرین بروزرسانی: {local:%Y/%m/%d - %H:%M}"]
    return "\n".join(lines)

def cycle(config, database, bale=None, publish=True):
    cycle_id = str(uuid4()); observations = [fetch(s, config.multipliers[s], config.fields.get(s,""), config.read_timeout, config.retries) for s in config.enabled if config.enabled[s]]
    average, valid = aggregate(observations, config.weights, config.min_sources, config.min_price, config.max_price, config.max_deviation)
    status = "success" if average is not None else "insufficient_sources"; database.run(cycle_id, observations, average, status, config.weights)
    if average is None: return None
    if bale and publish: bale.send(config.channel, format_message(average, valid, config))
    return average
