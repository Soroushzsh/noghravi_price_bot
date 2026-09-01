# Silver Price Bale Bot
## Product Requirements Document

**Version:** 1.0  
**Status:** Ready for implementation  
**Target:** Single Linux VPS  
**Primary language:** Python 3.12  
**Storage:** SQLite  
**Deployment:** Docker Compose  
**Output channel:** Bale

---

# 1. Objective

Build a small, reliable service that periodically retrieves the current price of **Silver 999** from four external Iranian price sources, normalizes all values to a common unit, validates them, calculates a configurable weighted average, stores the results in SQLite, and publishes the calculated price to a Bale channel.

The system should prioritize:

1. correctness,
2. operational simplicity,
3. resilience to individual API failures,
4. debuggability,
5. easy configuration,
6. low maintenance overhead.

This is intentionally **not** a distributed system.

Do not introduce Redis, PostgreSQL, Celery, Kafka, Kubernetes, Airflow, or a web framework unless future requirements genuinely require them.

---

# 2. Data Sources

The service consumes four APIs.

### Digikala

Endpoint:

`https://api.digikala.com/non-inventory/v1/prices/`

Silver value:

`silver999.price`

The current response exposes a `silver999` object containing `price` and `ttl`.

Initial normalization configuration:

`raw_price × 100 = Toman/gram`

This multiplier must remain configurable because the API itself does not provide an explicit unit in the response.

---

### Noghresea

Endpoint:

`https://api.noghresea.ir/api/market/getSilverPrice`

Silver value:

`price`

The public website describes its displayed silver value as a per-gram price in Toman, while the API currently returns values on a different numeric scale.

Initial normalization:

`raw_price × 1000 = Toman/gram`

Keep this multiplier configurable.

---

### Tokeniko

Endpoint:

`https://tokeniko.com/api/prices-with-change`

Find:

`products[].name == "Silver999"`

Default field:

`sellPrice`

The API currently exposes `buyPrice` and `sellPrice` for several silver purities including `Silver999`.

Initial normalization:

`raw_price × 0.1 = Toman/gram`

The selected field must be configurable:

`TOKENIKO_PRICE_FIELD=sellPrice`

Permitted values:

- `sellPrice`
- `buyPrice`

---

### Melligold

Endpoint:

`https://melligold.com/api/v1/exchange/buy-sell-price/?symbol=XAG&format=json`

Default field:

`data.price_buy`

The API exposes `price_buy` and `price_sell`. Melligold's public site identifies its silver instrument as **1 gram of Silver 999** priced in Toman.

Initial normalization:

`raw_price × 1 = Toman/gram`

Selected field must be configurable:

`MELLIGOLD_PRICE_FIELD=price_buy`

Permitted values:

- `price_buy`
- `price_sell`

---

# 3. Canonical Price

Every adapter must return the same internal representation:

- commodity: `silver`
- purity: `999`
- unit: `gram`
- currency: `IRT`
- price: decimal Toman value
- source
- fetched timestamp
- optional source timestamp
- raw value

Python calculations must use `Decimal`, **not binary floating point**, for price calculations.

Example internal object:

```text
PriceObservation
    source
    raw_price
    normalized_price_toman
    fetched_at
    source_timestamp
    latency_ms
```

---

# 4. Polling

Default polling interval:

`600 seconds`

Configuration:

`POLL_INTERVAL_SECONDS=600`

The application must:

1. start a polling cycle immediately after startup,
2. then run approximately every configured interval,
3. never run two cycles simultaneously,
4. continue operating indefinitely,
5. survive temporary source failures.

Changing the environment variable may require restarting the service.

Do **not** implement runtime configuration reload in v1.

Restarting a tiny service to apply configuration changes is acceptable and substantially simpler.

---

# 5. Source Weights

Each source has its own configurable weight.

Example:

```text
WEIGHT_DIGIKALA=1
WEIGHT_NOGHRESEA=1
WEIGHT_TOKENIKO=1
WEIGHT_MELLIGOLD=1
```

Weights do not need to sum to 1.

They must only be non-negative numbers.

The algorithm normalizes them automatically.

For valid prices:

`weighted_average = Σ(price × weight) / Σ(weight)`

A source with:

`weight = 0`

is effectively excluded from aggregation.

Prefer also supporting explicit source enable flags:

```text
DIGIKALA_ENABLED=true
NOGHRESEA_ENABLED=true
TOKENIKO_ENABLED=true
MELLIGOLD_ENABLED=true
```

---

# 6. Handling Failed Sources

Failure of one source must **never crash the polling service**.

Examples of source failure:

- connection timeout,
- DNS error,
- HTTP 500,
- HTTP 403,
- malformed JSON,
- expected field missing,
- returned value cannot be parsed,
- value is zero or negative,
- abnormal price,
- schema changed.

Each source should be fetched independently.

The weighted average should use only healthy sources:

`Σ(valid_price × configured_weight) / Σ(valid_weight)`

Therefore the remaining source weights are implicitly re-normalized.

Example:

If weights are:

```text
Digikala = 2
Noghresea = 1
Tokeniko = 1
Melligold = 1
```

and Digikala fails, the average uses the other three with total weight `3`.

---

# 7. Minimum Source Requirement

Add:

`MIN_VALID_SOURCES=3`

Default:

`3`

If fewer than three sources produce valid prices:

- do not publish a normal price,
- persist the failed aggregation attempt,
- emit an ERROR log,
- optionally notify an operations/admin Bale chat.

The service itself must continue running.

An optional separate variable should be supported:

`BALE_ALERT_CHAT_ID`

If it is not configured, operational failures are logged only.

Do not spam the public price channel with infrastructure errors by default.

---

# 8. Price Sanity Validation

An API returning HTTP 200 does not necessarily mean its price is correct.

The service must perform sanity checks before aggregation.

## Absolute range

Configurable:

```text
MIN_SILVER_PRICE_TOMAN=100000
MAX_SILVER_PRICE_TOMAN=2000000
```

Any value outside this range is invalid.

These limits exist mainly to catch unit/schema changes.

---

# 9. Outlier Detection

A source accidentally switching from Toman to Rial could corrupt the weighted average while still returning perfectly valid JSON.

Therefore implement median-based anomaly detection.

Configuration:

`MAX_SOURCE_DEVIATION_PCT=15`

Process:

1. collect normalized prices,
2. calculate their median,
3. calculate each source's percentage distance from the median,
4. exclude sources exceeding the configured threshold.

For example:

`deviation = abs(price - median) / median × 100`

Only perform median outlier detection when at least three candidates exist.

Excluded prices must still be stored in SQLite with an exclusion reason.

Example:

```text
excluded_reason = "deviation_from_median"
```

Log the event as WARNING.

---

# 10. HTTP Behavior

Use a shared `httpx.Client`.

Recommended defaults:

```text
HTTP_CONNECT_TIMEOUT_SECONDS=5
HTTP_READ_TIMEOUT_SECONDS=5
HTTP_MAX_RETRIES=2
```

Each source request should have limited retry with short exponential backoff.

Example:

- initial request
- retry after ~0.5 seconds
- retry after ~1.5 seconds

Do not retry indefinitely.

Do not allow one broken API to delay the entire cycle for minutes.

TLS certificate verification must remain enabled.

Set an identifiable User-Agent such as:

`silver-price-bale-bot/1.0`

---

# 11. Bale Integration

Use Bale's HTTP API directly.

Base URL:

`https://tapi.bale.ai/bot<token>/`

Bale documents `sendMessage` as accepting a `chat_id` that may also be a channel username such as `@channelusername`. Messages can contain between 1 and 4096 characters.

Required configuration:

```text
BALE_BOT_TOKEN=
BALE_CHANNEL_ID=@mychannel
```

The bot must have permission to publish messages to the target channel.

Do not log `BALE_BOT_TOKEN`.

At startup, call Bale's `getMe` method once to validate the bot token. Bale documents `getMe` specifically as a simple authentication-token test.

Failure of the startup `getMe` validation should fail application startup because publishing would otherwise be impossible.

---

# 12. Bale Message

Default output should remain simple.

Example:

```text
🥈 قیمت میانگین نقره ۹۹۹

۴۷۰٬۳۹۵ تومان / گرم

منابع معتبر: 4/4
آخرین بروزرسانی: ۱۴۰۵/۰۶/۰۳ - ۱۲:۰۰
```

Optionally include source breakdown through:

`INCLUDE_SOURCE_BREAKDOWN=true`

When enabled:

```text
🥈 قیمت میانگین نقره ۹۹۹

۴۷۰٬۳۹۵ تومان / گرم

دیجی‌کالا: ۴۸۶٬۶۰۰
نقره‌سی: ۴۵۵٬۸۲۰
توکنیکو: ۴۶۲٬۶۸۰
ملی‌گلد: ۴۷۶٬۴۷۸

منابع معتبر: 4/4
آخرین بروزرسانی: ۱۴۰۵/۰۶/۰۳ - ۱۲:۰۰
```

Do not expose weights in public messages unless explicitly enabled later.

---

# 13. Timezone

Database timestamps must be UTC.

Display timestamps should use:

`Asia/Tehran`

Configuration:

`DISPLAY_TIMEZONE=Asia/Tehran`

No database timestamps should be stored as ambiguous local times.

---

# 14. Publishing Policy

Polling and channel publishing are independent:

```text
SEND_CHANNEL_MESSAGE_ENABLED=true
SEND_CHANNEL_MESSAGE_INTERVAL=10800
SEND_CHANNEL_MESSAGE_CHANGE_THRESHOLD_PERCENT=0.5
```

The bot polls every `POLL_INTERVAL_SECONDS` and stores every cycle. A channel message is sent when channel messages are enabled and either no message has been published, the send interval has elapsed since the last successful publication, or the absolute aggregate-price change since the last successfully published message is strictly greater than the configured percentage threshold. The first successful aggregate is published immediately.

The threshold and displayed message percentage both use the last successfully published price as their baseline. Intervals are positive integer seconds; `10800` represents three hours. When channel messages are disabled, Bale credentials are not required and no threshold exception can trigger a send.

---

# 15. SQLite

SQLite is the required database.

Database path:

`/data/silver_price_bot.db`

Configuration:

`DATABASE_PATH=/data/silver_price_bot.db`

Initialize:

- WAL journal mode,
- foreign keys ON,
- busy timeout approximately 5 seconds.

Only one service process should write to the database.

Do not implement an ORM unless it clearly simplifies the implementation.

The standard `sqlite3` Python library is preferred for this small schema.

---

# 16. Database Schema

## aggregation_runs

Store one row per polling cycle.

Suggested fields:

```text
id
cycle_id
started_at
finished_at
status
weighted_average_toman
valid_source_count
candidate_source_count
total_effective_weight
published
bale_message_id
error_message
created_at
```

`cycle_id` should be a UUID.

Possible statuses:

```text
success
insufficient_sources
aggregation_failed
publish_failed
```

---

## source_observations

Store one row for every attempted source request.

Suggested fields:

```text
id
cycle_id
source
requested_at
received_at
latency_ms
http_status
raw_price
normalized_price_toman
configured_weight
selected_field
valid
excluded_reason
error_type
error_message
raw_response
created_at
```

Foreign key:

`cycle_id -> aggregation_runs.cycle_id`

Persist failed requests too.

This table is an audit trail and is extremely useful when investigating a wrong published price.

---

# 17. Raw Responses

Store API responses in `source_observations.raw_response`.

This makes it possible to determine later whether:

- the source schema changed,
- the value changed units,
- the wrong field was selected,
- normalization was incorrect.

Do not dump raw API responses into normal INFO logs.

They belong in SQLite.

At DEBUG level, truncated responses may optionally be logged.

---

# 18. Logging

Production logging must be structured and useful.

Configuration:

```text
LOG_LEVEL=INFO
LOG_FORMAT=json
```

Recommended events:

```text
service_started
config_validated
poll_cycle_started
source_fetch_started
source_fetch_success
source_fetch_failed
source_price_rejected
source_outlier_detected
aggregation_success
aggregation_failed
bale_publish_started
bale_publish_success
bale_publish_failed
poll_cycle_completed
service_stopping
```

Every cycle-related event should contain:

```text
cycle_id
```

Source-related events should additionally contain:

```text
source
latency_ms
http_status
normalized_price
```

Exceptions should include stack traces.

Secrets must always be redacted.

In production, logs should go to stdout/stderr so they are available through:

```text
docker compose logs
```

No custom ELK/Loki stack is required.

---

# 19. Application Architecture

Use a small modular architecture:

```text
src/
  silver_bot/
    __init__.py
    __main__.py
    config.py
    service.py
    scheduler.py
    aggregation.py
    database.py
    bale.py
    logging_config.py

    sources/
      __init__.py
      base.py
      digikala.py
      noghresea.py
      tokeniko.py
      melligold.py
```

Each price provider must be isolated behind the same interface.

Conceptually:

```text
PriceSource
    fetch() -> PriceObservation
```

Do not put API-specific JSON parsing inside the main service.

---

# 20. Source Adapter Responsibilities

Each source adapter is responsible for:

1. making its HTTP request,
2. validating HTTP response,
3. parsing JSON,
4. finding the correct price field,
5. converting the raw value to `Decimal`,
6. applying its normalization multiplier,
7. returning a standard observation.

The aggregation layer must have no knowledge of Digikala, Tokeniko, etc.

This isolation is important because these unofficial/public endpoints may change independently.

---

# 21. Configuration

Provide `.env.example`.

Minimum variables:

```text
# Polling
POLL_INTERVAL_SECONDS=600

# Bale
BALE_BOT_TOKEN=
BALE_CHANNEL_ID=
BALE_ALERT_CHAT_ID=

# Sources
DIGIKALA_ENABLED=true
NOGHRESEA_ENABLED=true
TOKENIKO_ENABLED=true
MELLIGOLD_ENABLED=true

# Weights
WEIGHT_DIGIKALA=1
WEIGHT_NOGHRESEA=1
WEIGHT_TOKENIKO=1
WEIGHT_MELLIGOLD=1

# Normalization
DIGIKALA_MULTIPLIER=100
NOGHRESEA_MULTIPLIER=1000
TOKENIKO_MULTIPLIER=0.1
MELLIGOLD_MULTIPLIER=1

# Fields
TOKENIKO_PRICE_FIELD=sellPrice
MELLIGOLD_PRICE_FIELD=price_buy

# Validation
MIN_VALID_SOURCES=3
MIN_SILVER_PRICE_TOMAN=100000
MAX_SILVER_PRICE_TOMAN=2000000
MAX_SOURCE_DEVIATION_PCT=15

# HTTP
HTTP_CONNECT_TIMEOUT_SECONDS=5
HTTP_READ_TIMEOUT_SECONDS=5
HTTP_MAX_RETRIES=2

# Output
DISPLAY_TIMEZONE=Asia/Tehran
INCLUDE_SOURCE_BREAKDOWN=true
SEND_CHANNEL_MESSAGE_ENABLED=true
SEND_CHANNEL_MESSAGE_INTERVAL=10800
SEND_CHANNEL_MESSAGE_CHANGE_THRESHOLD_PERCENT=0.5

# Persistence
DATABASE_PATH=/data/silver_price_bot.db

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

All configuration must be validated on application startup.

Invalid configuration should cause an immediate clear error.

Examples:

- negative weight,
- interval <= 0,
- invalid boolean,
- zero enabled sources,
- `MIN_VALID_SOURCES` larger than enabled sources,
- missing Bale token,
- missing Bale channel.

---

# 22. CLI

The application should support several operational commands.

## Run continuously

```text
python -m silver_bot run
```

## Execute exactly one cycle

```text
python -m silver_bot once
```

Useful during deployment.

## Fetch without publishing

```text
python -m silver_bot once --dry-run
```

This should:

- fetch all sources,
- print normalized values,
- calculate the weighted average,
- store results if appropriate,
- not contact `sendMessage`.

## Configuration/API diagnostic

```text
python -m silver_bot doctor
```

It should test:

- configuration,
- SQLite access,
- every enabled source,
- Bale `getMe`.

Output should clearly show which components are healthy.

---

# 23. Health Check

Provide:

```text
python -m silver_bot healthcheck
```

It should check SQLite for the latest successful polling cycle.

The service is healthy if the last successful cycle occurred within approximately:

`2.5 × POLL_INTERVAL_SECONDS`

Return:

- exit code `0` when healthy,
- nonzero otherwise.

Docker can use this command as its health check.

No HTTP health-check server is necessary.

---

# 24. Deployment

Primary deployment is Docker Compose.

Required files:

```text
Dockerfile
compose.yaml
.env.example
.dockerignore
```

The container should:

- run as a non-root user,
- expose no ports,
- mount `/data`,
- use `restart: unless-stopped`,
- have a health check,
- write logs to stdout/stderr.

Example persistent host directory:

```text
./data:/data
```

There is no reason for this service to accept inbound Internet traffic.

Only outbound HTTPS access is required.

This significantly reduces VPS attack surface.

---

# 25. SQLite Backup

Historical prices are useful, but losing them should not stop the service.

Document a simple SQLite backup process.

Use SQLite's backup functionality instead of blindly copying an actively written database file.

A daily or weekly backup is sufficient.

Keep this operational process documented rather than building a complex backup service into the application.

---

# 26. Graceful Shutdown

Handle at least:

- SIGTERM
- SIGINT

When Docker or the VPS stops the service:

1. stop scheduling new cycles,
2. allow the current short-running operation to complete where practical,
3. close HTTP client,
4. close SQLite connection,
5. emit `service_stopping`.

---

# 27. Dependencies

Keep runtime dependencies minimal.

Recommended:

```text
httpx
pydantic
pydantic-settings
```

Development:

```text
pytest
pytest-cov
```

Use Python's standard libraries for:

- sqlite,
- logging,
- datetime,
- signal handling,
- UUID generation,
- statistics.

Avoid APScheduler for v1 unless it demonstrably simplifies scheduling.

A simple monotonic-time polling loop is sufficient.

---

# 28. Automated Tests

Tests are mandatory.

## Adapter tests

Create stored JSON fixtures for all four source responses.

Test:

- successful parsing,
- missing fields,
- malformed numeric value,
- unexpected JSON,
- normalization.

## Aggregation tests

Test:

- all four sources successful,
- one source unavailable,
- zero-weight source,
- custom weights,
- source outlier,
- insufficient valid sources.

## Bale tests

Mock HTTP requests.

Test:

- successful message,
- API `ok=false`,
- timeout,
- HTTP error,
- malformed Bale response.

## Database tests

Test:

- schema initialization,
- observations stored,
- failed observations stored,
- aggregation stored,
- published message information updated.

---

# 29. Important Regression Test

Include a test specifically designed to prevent a unit-conversion disaster.

Given prices corresponding approximately to the same market level but represented using the four APIs' different scales, normalization must produce values in the same general range.

If one adapter accidentally returns a value approximately 10×, 100×, or 1000× the others, tests must fail.

This is one of the most important tests in the project.

---

# 30. Failure Scenarios

### Digikala down

Continue with other sources.

### Tokeniko changes JSON schema

Mark Tokeniko failed, persist raw response, log parsing error, continue.

### One source returns 10× price

Outlier detection excludes it.

### Two sources fail

If `MIN_VALID_SOURCES=3`, do not publish.

### Bale unavailable

Store successful aggregation with:

```text
status=publish_failed
```

Log failure.

Do not lose the calculated observation data.

The next scheduled cycle should continue normally.

### SQLite temporarily locked

Retry briefly using SQLite `busy_timeout`.

Unexpected persistent database errors should be logged at ERROR level.

### Service crashes

Docker automatically restarts it.

Next startup should execute a new cycle immediately.

---

# 31. Do Not Retry Old Bale Messages

Version 1 should **not** maintain a message delivery queue.

If Bale publishing fails at 12:00, do not send the stale 12:00 price at 12:10.

At 12:10 fetch fresh prices and attempt to publish the newest result.

For a market-price channel, freshness is more important than guaranteed delivery of historical messages.

---

# 32. Price Formatting

Never use floating-point formatting.

Use `Decimal`.

Before publishing:

- round according to configured display precision,
- use thousands separators,
- include `تومان`,
- include `/ گرم`.

Configuration:

```text
DISPLAY_DECIMAL_PLACES=0
```

Default output is integer Toman.

---

# 33. Security Requirements

The implementation must:

- never commit `.env`,
- never log Bale token,
- never include token in exceptions visible to users,
- use HTTPS,
- verify SSL certificates,
- run container as non-root,
- expose no network ports,
- pin sensible dependency versions,
- keep `.env.example` free from actual secrets.

The bot token should be treated as a password.

---

# 34. README Requirements

README must contain:

1. project purpose,
2. architecture,
3. requirements,
4. Bale bot setup,
5. instructions for adding the bot to the channel,
6. environment configuration,
7. local development,
8. `once --dry-run`,
9. Docker deployment,
10. checking logs,
11. health checks,
12. database location,
13. database backup,
14. troubleshooting,
15. explanation of normalization multipliers,
16. explanation of source weights,
17. how to add another price source.

---

# 35. Implementation Order

The AI implementation agent should work in this order:

1. create repository structure,
2. implement validated configuration,
3. implement common price-source model,
4. implement four source adapters,
5. add adapter fixtures/tests,
6. implement normalization,
7. implement sanity and outlier validation,
8. implement weighted aggregation,
9. implement SQLite persistence,
10. implement Bale client,
11. implement one-shot execution,
12. implement scheduler,
13. implement structured logging,
14. implement health check,
15. create Dockerfile/Compose,
16. write integration tests,
17. write README,
18. run complete test suite,
19. run `once --dry-run` against live sources,
20. only then perform a real test Bale publication.

---

# 36. Acceptance Criteria

The project is complete when all of these are true:

- [ ] Application starts with one Docker Compose command.
- [ ] No inbound ports are exposed.
- [ ] All four source APIs are queried independently.
- [ ] Every raw price is normalized to Silver 999 Toman/gram.
- [ ] Configured weights are used correctly.
- [ ] Failed sources are automatically excluded.
- [ ] Outlier prices are automatically excluded.
- [ ] Average is published only when the configured minimum number of sources is available.
- [ ] Every polling cycle is recorded in SQLite.
- [ ] Every source attempt, including failures, is recorded.
- [ ] Successful messages are sent to the configured Bale channel.
- [ ] Bale failures do not crash the service.
- [ ] Individual source failures do not crash the service.
- [ ] Logs contain enough information to diagnose every polling cycle.
- [ ] Bale token never appears in logs.
- [ ] `once --dry-run` works.
- [ ] `doctor` works.
- [ ] Docker health check works.
- [ ] Container automatically restarts after process/VPS restart.
- [ ] Automated tests cover normalization and aggregation.
- [ ] README contains complete deployment and troubleshooting instructions.

---

# 37. Explicit Non-Goals for v1

Do not implement:

- admin dashboard,
- HTTP REST API,
- user accounts,
- PostgreSQL,
- Redis,
- Celery,
- Kubernetes,
- Prometheus/Grafana,
- runtime configuration UI,
- Telegram,
- historical charts,
- price prediction,
- machine learning,
- complex message queue,
- guaranteed delivery,
- interactive Bale commands.

These can be added later if they solve an actual requirement.

---

# 38. Design Principle

The preferred architecture is:

```text
4 External APIs
      │
      ▼
Source Adapters
      │
      ▼
Normalization
      │
      ▼
Validation / Outlier Detection
      │
      ▼
Weighted Average
      │
      ├────────► SQLite
      │
      ▼
Bale sendMessage
      │
      ▼
Bale Channel
```

Everything runs inside **one Python process**.

For the expected workload, this is the desired architecture—not merely an MVP compromise.

The service should be boring, predictable, inspectable, and easy to recover when an external API inevitably changes.
