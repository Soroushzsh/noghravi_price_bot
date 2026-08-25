You are a senior full-stack software engineer, product designer, and technical architect.

Your task is to design and implement a **production-ready public website for “Noghre Time | نقره تایم”** alongside the existing Bale silver-price bot project.

You MUST use this UI/UX skill as your design system and implementation guidance:

`https://www.skills.sh/nextlevelbuilder/ui-ux-pro-max-skill/ui-ux-pro-max`

The website should be minimal, premium, trustworthy, data-first, fast, mobile-first, SEO-friendly, and suitable for an Iranian audience interested in silver prices, market trends, reports, and silver price predictions.

The existing bot project already:

* fetches silver prices from multiple Iranian sources,
* calculates a weighted reference silver price,
* fetches global XAG price,
* fetches USDT/IRT,
* calculates local/global comparisons,
* stores historical observations,
* sends updates to a Bale channel,
* uses Python,
* uses SQLite,
* runs on a VPS,
* is intentionally simple and operationally solid.

The website must extend this existing project without turning it into an unnecessarily complex distributed system.

# Product

Brand:

**Noghre Time**
**نقره تایم**

Positioning:

**مرجع قیمت، روند و تحلیل بازار نقره**

Core value proposition:

Users should be able to open the website and immediately understand:

* current Silver 999 price in Iran,
* global XAG price,
* fair/global-equivalent silver price in Toman,
* Iranian silver premium / discount,
* recent price trend,
* latest reports,
* latest silver market prediction,
* important market alerts.

The website should feel like a focused financial information product, not a generic news website.

# Primary user questions

The homepage should answer these questions within a few seconds:

1. قیمت هر گرم نقره ۹۹۹ الان چقدر است؟
2. قیمت نسبت به دیروز چقدر تغییر کرده؟
3. قیمت جهانی نقره چند است؟
4. قیمت فعلی بازار ایران نسبت به ارزش جهانی حباب دارد یا خیر؟
5. روند کوتاه‌مدت نقره صعودی، خنثی یا نزولی است؟
6. آخرین تحلیل نقره تایم چیست؟
7. داده‌ها چه زمانی به‌روزرسانی شده‌اند؟

# Technical philosophy

Keep the architecture simple.

Preferred architecture:

```text
Existing Python Bot / Price Collector
          │
          ▼
        SQLite
          │
          ├── Bale Publisher
          │
          └── Public Website API / Backend
                    │
                    ▼
              Public Website
```

Do NOT introduce unnecessary infrastructure.

Avoid by default:

* PostgreSQL
* Redis
* Kafka
* Celery
* Kubernetes
* microservices
* Elasticsearch
* complicated CMS systems

Use SQLite unless a real technical limitation is encountered.

The target deployment is a single VPS.

# Repository strategy

Prefer one repository with clear separation:

```text
noghre-time/
├── backend/
├── frontend/
├── data/
├── docker/
├── tests/
├── compose.yaml
├── .env.example
└── README.md
```

If the existing bot repository already has a good structure, extend it rather than rewriting everything.

Do not duplicate price-fetching logic between the website and the bot.

There must be one source of truth for price ingestion and calculations.

# Backend

Use the existing Python application.

Preferred backend framework for the website API:

**FastAPI**

The website API should be lightweight and read mostly from SQLite.

Do not move the polling logic into HTTP request handlers.

Price collection continues as a background process/service.

The website reads already-calculated data.

Suggested backend structure:

```text
backend/
  app/
    main.py
    config.py
    db.py
    models/
    repositories/
    services/
    api/
      routes/
        market.py
        history.py
        reports.py
        predictions.py
        health.py
```

# Frontend

Use:

* Next.js
* TypeScript
* React
* Tailwind CSS if compatible with the UI/UX skill
* server-side rendering or static/server hybrid rendering where useful
* responsive design
* accessible components

You MUST actively apply the principles and components from:

`ui-ux-pro-max`

Do not merely mention the skill.

Use it to drive:

* visual hierarchy,
* spacing,
* typography,
* interaction patterns,
* card design,
* navigation,
* responsive behavior,
* information density,
* color usage,
* chart presentation,
* UX states,
* mobile layout.

# Visual direction

Brand personality:

* premium
* calm
* analytical
* trustworthy
* modern
* minimal
* financial
* distinctly related to silver

Avoid:

* crypto-casino styling
* neon overload
* black/gold luxury clichés
* cluttered dashboards
* overly glossy finance UI
* excessive gradients
* too many cards
* ticker overload
* red/green everywhere

Suggested color direction:

* off-white / very light neutral background
* charcoal text
* silver / cool gray accents
* restrained dark mode
* green/red only for actual positive/negative changes

The interface should feel closer to a modern financial research product than a trading terminal.

# RTL and Persian

The primary language is Persian.

Implement proper RTL support.

Requirements:

* `<html dir="rtl" lang="fa">`
* RTL-aware layout
* correct number alignment
* proper mixed Persian/Latin text handling
* localized formatting
* Persian-friendly font stack
* mobile typography that remains readable

Use Persian digits where appropriate in presentation, but preserve raw numeric values internally.

English ticker names such as:

* XAG/USD
* USDT/IRT

should remain visually correct in RTL contexts.

# Homepage

The homepage is the most important page.

Suggested structure:

## 1. Header

Minimal header.

Include:

* Noghre Time logo
* قیمت نقره
* نمودار
* تحلیل‌ها
* پیش‌بینی
* درباره ما
* Bale CTA

CTA:

**دنبال کردن در بله**

Keep navigation minimal.

## 2. Hero market card

The first screen must prominently show:

**قیمت مرجع نقره ۹۹۹**

Example:

```text
۴۰۲٬۸۵۰ تومان
هر گرم نقره ۹۹۹

+۲.۴٪ امروز
```

Include:

* current reference price
* daily change
* timestamp
* freshness indicator

Example:

**آخرین بروزرسانی: ۲ دقیقه پیش**

Do not use fake real-time animations.

## 3. Market summary

Show compact metrics:

* XAG/USD
* USDT/IRT
* ارزش جهانی هر گرم
* حباب / پریمیوم نقره ایران

Example:

```text
اونس نقره
$67.42

تتر
۱۷۳٬۲۰۰ تومان

ارزش جهانی
۳۷۵٬۸۰۰ تومان

حباب نقره
+۷.۲٪
```

## 4. Silver premium section

This should be a signature feature of the product.

Explain:

**حباب نقره چیست؟**

Formula:

```text
Local Market Price
÷
Global Equivalent Price
− 1
```

Present it in user-friendly Persian.

Example:

**بازار ایران در حال حاضر ۷.۲٪ بالاتر از ارزش جهانی معامله می‌شود.**

Avoid implying investment advice.

## 5. Price chart

Provide a clean historical price chart.

Periods:

* 24 ساعت
* 7 روز
* 30 روز
* 3 ماه
* 1 سال

Metrics switcher:

* قیمت مرجع
* ارزش جهانی
* حباب

Do not overload the chart.

Mobile interaction is critical.

## 6. Market trend summary

Display the current trend classification:

* صعودی
* خنثی
* نزولی

Example:

```text
روند کوتاه‌مدت
صعودی ملایم

قیمت طی ۷ روز گذشته ۵.۸٪ افزایش داشته و
حباب بازار از ۳.۲٪ به ۵.۱٪ رسیده است.
```

Clearly label generated predictions/analysis as probabilistic and informational.

## 7. Latest prediction

Create a feature card:

**پیش‌بینی نقره تایم**

Include:

* prediction horizon
* direction
* confidence
* short reasoning
* publication timestamp

Example:

```text
چشم‌انداز ۷ روزه

صعودی ملایم

احتمال: ۶۲٪

محرک‌های اصلی:
رشد XAG
ثبات نسبی تتر
افزایش تقاضای داخلی
```

Add disclaimer:

**این تحلیل توصیه خرید یا فروش نیست.**

## 8. Latest reports

Show 3–6 recent reports.

Examples:

* چرا نقره امروز گران شد؟
* حباب نقره به بالاترین سطح ماه رسید
* بررسی روند XAG در هفته آینده
* تاثیر قیمت تتر بر بازار نقره ایران

Each report should have:

* title
* summary
* date
* category
* reading time

## 9. Source transparency

Important trust section.

Explain that the reference price is calculated from multiple sources.

Show source names and status:

```text
دیجی‌کالا        فعال
نقره‌سی          فعال
توکنیکو          فعال
ملی‌گلد           فعال
```

Do not expose internal secrets or unnecessary implementation details.

Explain:

**قیمت مرجع نقره تایم از ترکیب چند منبع بازار و حذف داده‌های غیرعادی محاسبه می‌شود.**

## 10. Bale CTA

Strong CTA:

**قیمت و هشدارهای مهم نقره را در بله دریافت کنید**

Button:

**عضویت در کانال نقره تایم**

# Other pages

Create the following routes:

```text
/
 /price
 /chart
 /reports
 /reports/[slug]
 /predictions
 /about
```

Potential future route:

```text
/calculator
```

Do not implement it unless it fits naturally into v1.

# `/price`

Dedicated market page.

Show:

* reference price
* source prices
* XAG/USD
* USDT
* fair global value
* premium
* daily high
* daily low
* 24h change
* 7d change
* last update time

# `/chart`

Larger interactive chart.

Compare:

* reference price
* global equivalent price

Optional secondary visualization:

premium percentage.

# `/reports`

Editorial/report list.

Filters:

* بازار ایران
* اونس جهانی
* تحلیل
* آموزش
* گزارش روزانه

# `/reports/[slug]`

SEO-optimized article page.

Include:

* title
* summary
* author / Noghre Time
* publish date
* updated date
* structured content
* related reports
* Bale CTA

# `/predictions`

Show latest predictions and historical prediction records.

Each prediction should include:

* published time
* forecast horizon
* expected direction
* probability/confidence
* expected range if available
* underlying inputs
* eventual outcome if prediction period has passed

This is important.

Do not delete old predictions.

Build credibility by preserving prediction history.

Later the product should be able to show:

**عملکرد پیش‌بینی‌های نقره تایم**

# Prediction model

Do not fabricate AI/ML sophistication.

Initially predictions may come from:

* human-created analysis,
* deterministic rules,
* an external AI-generated report,
* a future statistical model.

Design the data model so prediction provenance is stored.

Suggested fields:

```text
id
created_at
published_at
horizon
direction
confidence
target_low
target_high
summary
reasoning
source_type
model_name
status
actual_end_price
result
```

Possible `source_type`:

```text
manual
rule_based
llm
ml_model
```

# Reports data model

Create a simple SQLite table.

Suggested schema:

```text
reports

id
slug
title
summary
content
category
status
published_at
updated_at
seo_title
seo_description
created_at
```

Statuses:

```text
draft
published
archived
```

Do not build a full CMS.

For v1, reports may be inserted through:

* CLI
* SQL
* small internal script
* Markdown files imported into SQLite

Choose the simplest maintainable solution.

# Market API

Implement endpoints similar to:

```text
GET /api/v1/market/latest
GET /api/v1/market/sources
GET /api/v1/market/history
GET /api/v1/market/summary
GET /api/v1/reports
GET /api/v1/reports/{slug}
GET /api/v1/predictions/latest
GET /api/v1/predictions
GET /api/v1/health
```

# Example latest-market response

```json
{
  "reference_price_toman": 402850,
  "change_24h_pct": 2.41,
  "xag_usd": 67.42,
  "usdt_toman": 173200,
  "global_value_toman": 375800,
  "premium_pct": 7.20,
  "valid_sources": 4,
  "total_sources": 4,
  "updated_at": "2026-08-25T16:50:00Z"
}
```

# Historical API

Support range parameters.

Example:

```text
GET /api/v1/market/history?range=7d
```

Valid values:

```text
24h
7d
30d
90d
1y
```

Avoid returning excessive raw data points.

Downsample when necessary.

For example:

* 24h → 10-minute samples
* 7d → hourly
* 30d → 4-hour
* 1y → daily

# Database

Continue using SQLite.

Enable:

* WAL mode
* indexes for time-range queries
* indexes on report slug and publish timestamp
* indexes on prediction publish timestamp

Keep raw observations and public aggregated prices separate.

Suggested public price table:

```text
market_snapshots

id
timestamp
reference_price_toman
xag_usd
usdt_toman
global_value_toman
premium_pct
valid_sources
created_at
```

This gives the frontend a stable, easy-to-query historical dataset.

# Data ingestion

Do not make the frontend scrape APIs.

External source ingestion must remain backend-only.

The flow is:

```text
External Sources
    ↓
Python adapters
    ↓
Validation
    ↓
Weighted aggregation
    ↓
SQLite market_snapshots
    ↓
FastAPI
    ↓
Next.js
```

# Performance

Target:

* Lighthouse Performance > 90 on mobile
* minimal JavaScript
* server rendering where useful
* lazy-load charts
* optimized fonts
* optimized images
* no huge UI frameworks unless justified

# SEO

SEO is a major acquisition channel.

Optimize for Persian search terms such as:

* قیمت نقره
* قیمت نقره امروز
* قیمت نقره ۹۹۹
* قیمت هر گرم نقره
* قیمت انس نقره
* اونس نقره
* حباب نقره
* نمودار قیمت نقره
* پیش بینی قیمت نقره
* تحلیل نقره

Implement:

* title templates
* meta descriptions
* canonical URLs
* OpenGraph
* Twitter/X metadata
* sitemap.xml
* robots.txt
* JSON-LD where appropriate

Avoid keyword stuffing.

# Structured metadata

Use appropriate schema.org types when valid:

* Organization
* WebSite
* Article
* BreadcrumbList

Do not falsely mark financial predictions as factual market data.

# PWA

Do not build a full PWA unless it is nearly free from the chosen stack.

A responsive mobile website is more important.

# Analytics

Prepare an optional lightweight analytics integration.

Do not hardcode a provider.

Configuration example:

```text
ANALYTICS_ENABLED=false
ANALYTICS_PROVIDER=
ANALYTICS_SITE_ID=
```

# Trust and disclaimers

The site must clearly distinguish between:

1. market data,
2. computed reference values,
3. analysis,
4. predictions.

Use wording like:

**قیمت مرجع نقره تایم یک شاخص محاسباتی بر اساس چند منبع بازار است و الزاماً قیمت قابل معامله در هیچ فروشگاه مشخصی نیست.**

For predictions:

**تحلیل‌ها و پیش‌بینی‌های نقره تایم صرفاً با هدف اطلاع‌رسانی منتشر می‌شوند و توصیه سرمایه‌گذاری، خرید یا فروش نیستند.**

# Error states

Design excellent UX for:

* no data yet
* stale prices
* one source down
* chart unavailable
* API unavailable
* no reports
* no prediction published

Never display `0` as a valid market price.

When data is stale, visibly show:

**اطلاعات با تاخیر به‌روزرسانی شده است**

# Freshness

Use backend timestamps.

Do not fake live updates in the browser.

Frontend should render:

* `چند لحظه پیش`
* `۲ دقیقه پیش`
* `۱۲ دقیقه پیش`

If older than an acceptable threshold, display a warning.

# Dark mode

Implement light and dark modes if compatible with the UI skill and not overly costly.

Do not let dark mode become the primary design gimmick.

Persist user preference locally.

# Charts

Use a lightweight React-compatible chart library.

Requirements:

* responsive
* touch-friendly
* Persian/RTL labels
* readable tooltips
* no unnecessary 3D
* no excessive animation

Include:

* exact timestamp
* price
* percentage change where relevant

# Accessibility

Must include:

* semantic HTML
* keyboard navigation
* adequate contrast
* focus states
* accessible chart descriptions
* `aria-label` where useful
* reduced-motion support

# Testing

Backend:

* pytest
* API endpoint tests
* database tests
* time-range query tests
* stale-data tests

Frontend:

* component tests where useful
* route smoke tests
* basic accessibility checks

Critical end-to-end paths:

1. Homepage renders latest market data.
2. Chart loads historical data.
3. Report page renders by slug.
4. Prediction page renders.
5. Bale CTA works.
6. Backend unavailable state is handled gracefully.

# Docker deployment

The entire project should deploy with:

```text
docker compose up -d --build
```

Suggested services:

```text
price-worker
backend
frontend
```

All may share the same SQLite volume where appropriate.

Be careful with SQLite concurrency.

The worker should be the primary writer for market observations.

Backend should mostly read.

If reports/predictions require writes, use short transactions and WAL mode.

# Reverse proxy

Use Caddy or Nginx.

Prefer Caddy if starting from scratch because TLS is simpler.

Expose only:

* 80
* 443

Do not expose backend or SQLite directly.

Architecture:

```text
Internet
   ↓
Caddy
   ↓
Next.js
   ↓
FastAPI
   ↓
SQLite
```

# Domain

Assume a domain such as:

```text
noghretime.ir
```

but make domain configurable.

Do not hardcode it throughout the source.

# Security

Requirements:

* run containers as non-root where possible
* no secrets in repository
* `.env` ignored
* API not unnecessarily exposed
* security headers
* HTTPS
* strict input validation
* parameterized SQL
* rate-limit public API endpoints if abuse becomes possible
* disable backend API docs in production if desired
* do not expose raw upstream API responses publicly

# Development quality

Act as a senior engineer.

Do not produce prototype-quality code.

Requirements:

* type hints
* clear module boundaries
* minimal but useful comments
* consistent naming
* no dead code
* no giant files
* meaningful exceptions
* structured logs
* environment validation
* graceful shutdown
* deterministic migrations/schema initialization
* testable business logic

# UI workflow

Before implementing the UI:

1. inspect and understand the `ui-ux-pro-max` skill,
2. identify the most appropriate visual patterns,
3. create a concise design direction,
4. create the homepage information architecture,
5. create reusable component hierarchy,
6. then implement.

Do not start by randomly styling components.

# Required reusable frontend components

At minimum:

```text
Header
MobileNavigation
MarketHero
MetricCard
PremiumIndicator
TrendBadge
PriceChart
SourceStatus
PredictionCard
ReportCard
FreshnessIndicator
BaleCTA
Footer
EmptyState
ErrorState
SkeletonState
```

# Responsive requirements

Design explicitly for:

* 360px mobile
* 390px mobile
* tablet
* desktop
* large desktop

The mobile homepage must remain useful without excessive scrolling before showing the main price.

The market price must be visible above the fold.

# UX priority order

When tradeoffs arise, prioritize:

1. price clarity
2. data trust
3. mobile usability
4. speed
5. readability
6. visual polish
7. feature density

# Initial implementation scope

Implement these features now:

* homepage
* latest silver price
* XAG/USD
* USDT/IRT
* global fair-value calculation
* silver premium
* historical chart
* latest reports
* latest prediction
* reports list
* report detail
* predictions page
* about page
* Bale CTA
* SEO
* responsive design
* production Docker setup
* logs
* health check
* tests

Do not implement:

* login
* subscriptions
* payments
* personalized alerts
* admin dashboard
* comments
* forums
* portfolios
* user accounts

Design the architecture so these can be added later without rewriting the core.

# Acceptance criteria

The work is complete when:

* [ ] Existing bot functionality still works.
* [ ] Website uses the existing price pipeline rather than duplicate scrapers.
* [ ] Homepage clearly shows current Silver 999 reference price.
* [ ] XAG/USD is displayed.
* [ ] USDT/IRT is displayed.
* [ ] Global-equivalent Toman/gram value is displayed.
* [ ] Silver premium is calculated and displayed.
* [ ] Historical chart works.
* [ ] Reports system works.
* [ ] Predictions system works.
* [ ] Old predictions remain visible.
* [ ] Proper Persian RTL UX is implemented.
* [ ] Mobile experience is polished.
* [ ] UI follows `ui-ux-pro-max`.
* [ ] SEO metadata is implemented.
* [ ] Bale channel CTA is implemented.
* [ ] SQLite remains the primary datastore.
* [ ] No unnecessary infrastructure is introduced.
* [ ] Docker Compose deploys the full system.
* [ ] HTTPS/reverse-proxy deployment is documented.
* [ ] Health checks exist.
* [ ] Structured logs exist.
* [ ] Automated tests pass.
* [ ] README includes full local and VPS deployment instructions.

# Final deliverables

Produce and implement:

1. architecture summary,
2. final repository structure,
3. database schema/migrations,
4. backend implementation,
5. frontend implementation,
6. visual design based on `ui-ux-pro-max`,
7. responsive behavior,
8. Dockerfiles,
9. Docker Compose,
10. reverse-proxy configuration,
11. `.env.example`,
12. tests,
13. README,
14. production deployment instructions,
15. sample screenshots or visual verification if your environment supports it.

Do not stop at a design proposal.

**Implement the actual working website and integrate it with the existing Noghre Time bot project.**

When making engineering choices, default to the simplest production-worthy approach that can run reliably on one VPS.

The final result should feel like a focused Iranian silver market product that could credibly grow into a trusted price, analysis, prediction, alert, and financial-data platform.
