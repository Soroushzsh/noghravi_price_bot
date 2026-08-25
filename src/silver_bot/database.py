import sqlite3

SCHEMA = """CREATE TABLE IF NOT EXISTS aggregation_runs (id INTEGER PRIMARY KEY, cycle_id TEXT UNIQUE, started_at TEXT, finished_at TEXT, status TEXT, weighted_average_toman TEXT, valid_source_count INTEGER, candidate_source_count INTEGER, total_effective_weight TEXT, published INTEGER DEFAULT 0, bale_message_id TEXT, error_message TEXT, created_at TEXT); CREATE TABLE IF NOT EXISTS source_observations (id INTEGER PRIMARY KEY, cycle_id TEXT REFERENCES aggregation_runs(cycle_id), source TEXT, requested_at TEXT, received_at TEXT, latency_ms INTEGER, http_status INTEGER, raw_price TEXT, normalized_price_toman TEXT, configured_weight TEXT, selected_field TEXT, valid INTEGER, excluded_reason TEXT, error_type TEXT, error_message TEXT, raw_response TEXT, created_at TEXT);"""
class Database:
    def __init__(self, path):
        self.db = sqlite3.connect(path, timeout=5); self.db.execute("PRAGMA journal_mode=WAL"); self.db.execute("PRAGMA foreign_keys=ON"); self.db.execute("PRAGMA busy_timeout=5000"); self.db.executescript(SCHEMA); self.db.commit()
    def close(self): self.db.close()
    def latest_success(self): return self.db.execute("SELECT finished_at FROM aggregation_runs WHERE status='success' ORDER BY id DESC LIMIT 1").fetchone()
    def run(self, cycle, observations, average, status, weights):
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat(); self.db.execute("INSERT INTO aggregation_runs(cycle_id,started_at,finished_at,status,weighted_average_toman,valid_source_count,candidate_source_count,total_effective_weight,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (cycle, now, now, status, str(average) if average else None, sum(o.price is not None and not o.excluded for o in observations), sum(o.price is not None for o in observations), str(sum((weights[o.source] for o in observations if o.price is not None and not o.excluded), 0)), now))
        for o in observations: self.db.execute("INSERT INTO source_observations(cycle_id,source,latency_ms,http_status,raw_price,normalized_price_toman,configured_weight,valid,excluded_reason,error_message,raw_response,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (cycle,o.source,o.latency_ms,o.http_status,str(o.raw) if o.raw else None,str(o.price) if o.price else None,str(weights[o.source]),int(o.price is not None and not o.excluded),o.excluded,o.error,o.raw_response,now))
        self.db.commit()
