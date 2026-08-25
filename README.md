# Silver Price Bale Bot

Small Python 3.12 service that fetches Silver 999 prices from four public Iranian APIs plus the global XAG spot price, normalizes local prices to Toman/gram, rejects invalid/outlier values, stores an SQLite audit trail, and publishes the weighted average to Bale.

## Deploy on Ubuntu VPS

Install Docker and Compose, then:

```sh
cp .env.example .env
mkdir -p data
# edit .env and set BALE_BOT_TOKEN and BALE_CHANNEL_ID
docker compose up --build -d
docker compose logs -f
```

The container has no inbound ports, runs as an unprivileged user, restarts automatically, and persists the database at `./data/silver_price_bot.db`. Add the bot as an administrator of the Bale channel. Use `docker compose exec silver-bot python -m silver_bot healthcheck` to verify the latest successful cycle.

## Local commands

With `PYTHONPATH=src` and a configured `.env`: `python -m silver_bot once --dry-run`, `python -m silver_bot doctor`, or `python -m silver_bot run`. Configuration defaults and source multipliers are documented in `.env.example` and the PRD.

Back up SQLite with the SQLite backup API (for example, `sqlite3 data/silver_price_bot.db ".backup 'backup.db'"`) while the service is running.

The channel’s `🌍 XAG` line comes from Gold API’s free, unauthenticated USD-per-troy-ounce endpoint. If that external quote is unavailable, the local silver message is still published without the line.

Premium (حباب) is calculated as each valid Iranian source price minus the global XAG price converted with the configured USDT quote: `XAG USD/oz × USDT Toman/USD ÷ 31.1034768`. The message includes each source premium and the same-weighted average premium; missing global inputs omit premium lines without blocking publication.
