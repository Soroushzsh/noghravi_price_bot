from decimal import Decimal
from silver_bot.aggregation import aggregate
from silver_bot.sources import Observation
from silver_bot.sources import _extract
from silver_bot.service import format_message
def test_weighted_average_and_outlier():
    obs = [Observation(str(i), price=Decimal(v)) for i,v in enumerate((100,101,99,1000))]
    avg, valid = aggregate(obs, {str(i):Decimal(1) for i in range(4)}, 3, Decimal(1), Decimal(2000), Decimal(15))
    assert avg == Decimal(100)
    assert obs[3].excluded == "deviation_from_median"

def test_digikala_current_response_shape():
    assert _extract("digikala", {"silver999": {"price": 4823}}, "") == 4823

def test_message_shows_percentage_change():
    class Config: timezone = "Asia/Tehran"; breakdown = False
    message = format_message(Decimal("110"), [Observation("digikala", price=Decimal("110"))], Config(), Decimal("100"))
    assert "🟢 +10.00%" in message

def test_message_includes_usdt_price():
    class Config: timezone = "Asia/Tehran"; breakdown = False
    message = format_message(Decimal("100"), [], Config(), usdt_price=Decimal("199043"))
    assert "💵 دلار (USDT): ۱۹۹٬۰۴۳ تومان" in message
