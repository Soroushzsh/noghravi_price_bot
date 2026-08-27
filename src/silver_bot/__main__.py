import argparse, logging, os, signal, time
from datetime import datetime, timezone
from .config import Config
from .database import Database
from .bale import Bale
from .service import cycle

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=["run","once","doctor","healthcheck","init-db"]); parser.add_argument("--dry-run", action="store_true"); args = parser.parse_args()
    if args.command == "init-db":
        Database(os.getenv("DATABASE_PATH", "/data/silver_price_bot.db")).close()
        print(f"SQLite ready: {os.getenv('DATABASE_PATH', '/data/silver_price_bot.db')}")
        return
    logging.basicConfig(level=getattr(logging, Config.from_env().log_level.upper(), logging.INFO), format="%(asctime)s %(levelname)s %(message)s")
    config = Config.from_env(); db = Database(config.database)
    try:
        if args.command == "healthcheck":
            row = db.latest_success()
            healthy = False
            if row:
                try: healthy = (datetime.now(timezone.utc) - datetime.fromisoformat(row[0])).total_seconds() <= config.poll_interval * 2.5
                except ValueError: pass
            raise SystemExit(0 if healthy else 1)
        bale = Bale(config.token) if config.send_enabled else None
        if args.command == "doctor":
            if bale: bale.validate()
            print("configuration, SQLite and Bale OK" if bale else "configuration and SQLite OK (channel messages disabled)")
            return
        if args.command == "once": cycle(config, db, None if args.dry_run else bale, not args.dry_run); return
        if bale: bale.validate()
        stop = False
        def shutdown(*_): nonlocal stop; stop = True
        signal.signal(signal.SIGTERM, shutdown); signal.signal(signal.SIGINT, shutdown)
        while not stop:
            try: cycle(config, db, bale)
            except Exception: logging.exception("poll cycle failed")
            if not stop: time.sleep(config.poll_interval)
    finally: db.close()
if __name__ == "__main__": main()
