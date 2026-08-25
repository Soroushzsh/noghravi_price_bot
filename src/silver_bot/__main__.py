import argparse, logging, signal, time
from datetime import datetime, timezone
from .config import Config
from .database import Database
from .bale import Bale
from .service import cycle

def main():
    parser = argparse.ArgumentParser(); parser.add_argument("command", choices=["run","once","doctor","healthcheck"]); parser.add_argument("--dry-run", action="store_true"); args = parser.parse_args()
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
        bale = Bale(config.token)
        if args.command == "doctor": bale.validate(); print("configuration, SQLite and Bale OK"); return
        if args.command == "once": cycle(config, db, None if args.dry_run else bale, not args.dry_run); return
        bale.validate(); stop = False
        def shutdown(*_): nonlocal stop; stop = True
        signal.signal(signal.SIGTERM, shutdown); signal.signal(signal.SIGINT, shutdown)
        while not stop:
            try: cycle(config, db, bale)
            except Exception: logging.exception("poll cycle failed")
            if not stop: time.sleep(config.poll_interval)
    finally: db.close()
if __name__ == "__main__": main()
