from decimal import Decimal
from silver_bot.aggregation import aggregate
from silver_bot.sources import Observation
from silver_bot.sources import _extract
def test_weighted_average_and_outlier():
    obs = [Observation(str(i), price=Decimal(v)) for i,v in enumerate((100,101,99,1000))]
    avg, valid = aggregate(obs, {str(i):Decimal(1) for i in range(4)}, 3, Decimal(1), Decimal(2000), Decimal(15))
    assert avg == Decimal(100)
    assert obs[3].excluded == "deviation_from_median"

def test_digikala_current_response_shape():
    assert _extract("digikala", {"silver999": {"price": 4823}}, "") == 4823
