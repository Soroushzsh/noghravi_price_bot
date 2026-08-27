import sqlite3
from datetime import datetime
from decimal import Decimal

SCHEMA = """CREATE TABLE IF NOT EXISTS aggregation_runs (id INTEGER PRIMARY KEY, cycle_id TEXT UNIQUE, started_at TEXT, finished_at TEXT, status TEXT, weighted_average_toman TEXT, valid_source_count INTEGER, candidate_source_count INTEGER, total_effective_weight TEXT, published INTEGER DEFAULT 0, bale_message_id TEXT, error_message TEXT, xag_usd_per_oz TEXT, usdt_toman_per_usd TEXT, global_price_toman TEXT, weighted_premium_toman TEXT, weighted_premium_percent TEXT, created_at TEXT); CREATE TABLE IF NOT EXISTS source_observations (id INTEGER PRIMARY KEY, cycle_id TEXT REFERENCES aggregation_runs(cycle_id), source TEXT, requested_at TEXT, received_at TEXT, latency_ms INTEGER, http_status INTEGER, raw_price TEXT, normalized_price_toman TEXT, configured_weight TEXT, selected_field TEXT, valid INTEGER, excluded_reason TEXT, error_type TEXT, error_message TEXT, raw_response TEXT, premium_toman TEXT, premium_percent TEXT, created_at TEXT);"""
class Database:
    def __init__(self, path):
        self.db = sqlite3.connect(path, timeout=5); self.db.execute("PRAGMA journal_mode=WAL"); self.db.execute("PRAGMA foreign_keys=ON"); self.db.execute("PRAGMA busy_timeout=5000"); self.db.executescript(SCHEMA); self._ensure_columns(); self.db.commit()
    def _ensure_columns(self):
        required = {"aggregation_runs": ("xag_usd_per_oz", "usdt_toman_per_usd", "global_price_toman", "weighted_premium_toman", "weighted_premium_percent"), "source_observations": ("premium_toman", "premium_percent")}
        for table, columns in required.items():
            existing = {row[1] for row in self.db.execute(f"PRAGMA table_info({table})")}
            for column in columns:
                if column not in existing: self.db.execute(f"ALTER TABLE {table} ADD COLUMN {column} TEXT")
    def close(self): self.db.close()
    def latest_success(self): return self.db.execute("SELECT finished_at FROM aggregation_runs WHERE status='success' ORDER BY id DESC LIMIT 1").fetchone()
    def latest_average(self):
        row = self.db.execute("SELECT weighted_average_toman FROM aggregation_runs WHERE status='success' AND weighted_average_toman IS NOT NULL ORDER BY id DESC LIMIT 1").fetchone()
        return Decimal(row[0]) if row else None
    def latest_published(self):
        row = self.db.execute("SELECT weighted_average_toman, finished_at FROM aggregation_runs WHERE status='success' AND published=1 ORDER BY id DESC LIMIT 1").fetchone()
        return (Decimal(row[0]), datetime.fromisoformat(row[1])) if row else None
    def mark_published(self, cycle, message_id=None):
        self.db.execute("UPDATE aggregation_runs SET published=1, bale_message_id=? WHERE cycle_id=?", (message_id, cycle)); self.db.commit()
    def run(self, cycle, observations, average, status, weights, xag_price=None, usdt_price=None, premium=None):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat(); items = {item["source"]: item for item in premium["items"]} if premium else {}
        self.db.execute("INSERT INTO aggregation_runs(cycle_id,started_at,finished_at,status,weighted_average_toman,valid_source_count,candidate_source_count,total_effective_weight,xag_usd_per_oz,usdt_toman_per_usd,global_price_toman,weighted_premium_toman,weighted_premium_percent,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (cycle, now, now, status, str(average) if average else None, sum(o.price is not None and not o.excluded for o in observations), sum(o.price is not None for o in observations), str(sum((weights[o.source] for o in observations if o.price is not None and not o.excluded), 0)), str(xag_price) if xag_price else None, str(usdt_price) if usdt_price else None, str(premium["global"]) if premium else None, str(premium["weighted_absolute"]) if premium else None, str(premium["weighted_percent"]) if premium else None, now))
        for o in observations:
            item = items.get(o.source, {})
            self.db.execute("INSERT INTO source_observations(cycle_id,source,latency_ms,http_status,raw_price,normalized_price_toman,configured_weight,valid,excluded_reason,error_message,raw_response,premium_toman,premium_percent,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (cycle,o.source,o.latency_ms,o.http_status,str(o.raw) if o.raw else None,str(o.price) if o.price else None,str(weights[o.source]),int(o.price is not None and not o.excluded),o.excluded,o.error,o.raw_response,str(item["absolute"]) if item else None,str(item["percent"]) if item else None,now))
        self.db.commit()
