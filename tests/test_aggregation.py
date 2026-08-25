from decimal import Decimal
from silver_bot.aggregation import aggregate, calculate_premiums
from silver_bot.sources import Observation
from silver_bot.sources import _extract, _extract_xag
from silver_bot.service import format_message
from silver_bot.database import Database
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

def test_xag_parser_and_message():
    assert _extract_xag({"currency": "USD", "symbol": "XAG", "price": 68.157997}) == Decimal("68.157997")
    class Config: timezone = "Asia/Tehran"; breakdown = False
    message = format_message(Decimal("100"), [], Config(), xag_price=Decimal("68.157997"))
    assert "🌍 XAG: $68.16 / oz" in message

def test_weighted_premiums():
    observations = [Observation("a", price=Decimal("110")), Observation("b", price=Decimal("90"))]
    result = calculate_premiums(observations, Decimal("100"), {"a": Decimal("2"), "b": Decimal("1")})
    assert result["weighted_absolute"] == Decimal("3.333333333333333333333333333")
    assert result["weighted_percent"] == Decimal("3.333333333333333333333333333")

def test_message_includes_premiums():
    class Config: timezone = "Asia/Tehran"; breakdown = True
    premium = {"global": Decimal("100"), "items": [{"source": "digikala", "absolute": Decimal("10"), "percent": Decimal("10")}], "weighted_absolute": Decimal("10"), "weighted_percent": Decimal("10")}
    message = format_message(Decimal("110"), [Observation("digikala", price=Decimal("110"))], Config(), premium=premium)
    assert "📊 حباب میانگین وزنی: +۱۰ تومان (+۱۰٫۰۰%)" in message
    assert "• دیجی‌کالا: +۱۰٫۰۰% | ۱۱۰ تومان" in message
    assert "قیمت مرجع" not in message

def test_database_stores_premium_fields(tmp_path):
    db = Database(str(tmp_path / "prices.db"))
    observations = [Observation("digikala", price=Decimal("110"), raw=Decimal("110"))]
    premium = {"global": Decimal("100"), "items": [{"source": "digikala", "absolute": Decimal("10"), "percent": Decimal("10")}], "weighted_absolute": Decimal("10"), "weighted_percent": Decimal("10")}
    db.run("cycle", observations, Decimal("110"), "success", {"digikala": Decimal("1")}, Decimal("68"), Decimal("200000"), premium)
    run = db.db.execute("select xag_usd_per_oz, usdt_toman_per_usd, global_price_toman, weighted_premium_toman, weighted_premium_percent from aggregation_runs").fetchone()
    source = db.db.execute("select premium_toman, premium_percent from source_observations").fetchone()
    assert run == ("68", "200000", "100", "10", "10")
    assert source == ("10", "10")
    db.close()
