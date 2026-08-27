from decimal import Decimal

import pytest
from django.test import Client
from django.db import connection
from django.utils import timezone

from silver_bot.database import Database
from silver_bot.sources import Observation
from website.models import Report


@pytest.fixture
def bot_database(db):
    connection.ensure_connection()
    path = connection.connection.execute("PRAGMA database_list").fetchone()[2]
    db = Database(path)
    yield db
    db.close()


def test_public_routes_render_without_market_data(bot_database):
    client = Client(HTTP_HOST="localhost")
    for path in ("/", "/price/", "/chart/", "/reports/", "/predictions/", "/about/"):
        assert client.get(path).status_code == 200


def test_history_rejects_unknown_range(bot_database):
    assert Client(HTTP_HOST="localhost").get("/api/v1/market/history?range=bad").status_code == 400


def test_report_is_public_only_after_publish(bot_database):
    report = Report.objects.create(slug="draft-report", title="Draft", summary="Summary", content_markdown="# Draft", category="analysis")
    client = Client(HTTP_HOST="localhost")
    assert client.get(f"/reports/{report.slug}/").status_code == 404
    report.status = "published"
    report.published_at = timezone.now()
    report.save()
    assert client.get(f"/reports/{report.slug}/").status_code == 200


def test_latest_market_serializes_existing_worker_data(bot_database):
    observations = [Observation("digikala", raw=Decimal("400"), price=Decimal("400"))]
    bot_database.run("website-cycle", observations, Decimal("400"), "success", {"digikala": Decimal("1")}, Decimal("67.42"), Decimal("173200"), {"global": Decimal("375"), "items": [], "weighted_absolute": Decimal("25"), "weighted_percent": Decimal("6.66")})
    response = Client(HTTP_HOST="localhost").get("/api/v1/market/latest")
    assert response.status_code == 200
    assert response.json()["data"]["reference_price_toman"] == 400
    assert response.json()["data"]["xag_usd"] == 67.42
