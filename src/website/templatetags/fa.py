from decimal import Decimal
from django import template

register = template.Library()
TRANSLATION = str.maketrans("0123456789.", "۰۱۲۳۴۵۶۷۸۹٫")


@register.filter
def fa_number(value):
    if value is None or value == "":
        return "—"
    if isinstance(value, str):
        return value.translate(TRANSLATION)
    return f"{value:,}".replace(",", "٬").translate(TRANSLATION)


@register.filter
def fa_percent(value):
    if value is None or value == "":
        return "—"
    value = Decimal(str(value))
    sign = "+" if value > 0 else "" if value == 0 else "−"
    return f"{sign}{abs(value):.2f}%".replace(".", "٫").translate(TRANSLATION)


@register.filter
def direction_class(value):
    return {"up": "positive", "down": "negative", "flat": "neutral"}.get(value, "neutral")
