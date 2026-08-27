from datetime import datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

from silver_bot.database import Database
from silver_bot.service import should_publish


def config(enabled=True, interval=10800, threshold="0.5"):
    return SimpleNamespace(send_enabled=enabled, send_interval=interval, send_threshold_percent=Decimal(threshold))


def test_publishing_policy_uses_last_published_baseline():
    now = datetime.now(timezone.utc)
    last = (Decimal("100"), now - timedelta(seconds=3600))
    assert not should_publish(config(), Decimal("100.4"), last, now)
    assert should_publish(config(), Decimal("100.51"), last, now)
    assert should_publish(config(), Decimal("99.49"), last, now)


def test_publishing_policy_sends_first_and_when_interval_is_due():
    now = datetime.now(timezone.utc)
    assert should_publish(config(), Decimal("100"), None, now)
    last = (Decimal("100"), now - timedelta(seconds=10800))
    assert should_publish(config(), Decimal("100"), last, now)


def test_disabled_publishing_never_sends():
    now = datetime.now(timezone.utc)
    last = (Decimal("100"), now - timedelta(days=1))
    assert not should_publish(config(False), Decimal("200"), last, now)


def test_database_tracks_successful_publication(tmp_path):
    db = Database(str(tmp_path / "prices.db"))
    db.run("cycle", [], Decimal("100"), "success", {})
    assert db.latest_published() is None
    db.mark_published("cycle", "42")
    assert db.latest_published()[0] == Decimal("100")
    assert db.db.execute("select bale_message_id from aggregation_runs").fetchone()[0] == "42"
    db.close()
