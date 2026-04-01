# CLAUDE.md — PE Public Comps Engine

This file gives Claude context about this project so it can assist effectively without re-reading all source files from scratch on every session.

---

## What This Project Does

Automated public comparable company (comps) benchmarking platform for private equity use cases. Ingests daily stock prices and quarterly financial data for 100 S&P 500 equities, computes valuation multiples (EV/EBITDA, EV/Revenue, P/E), and aggregates them by GICS sector. Runs entirely within Snowflake.

**The core output:** `comps_gold.public.fct_daily_multiples` — one row per ticker per trading day with all valuation multiples computed. `comps_gold.public.agg_sector_multiples` — daily sector medians and IQR.

---

## Stack

| Layer | Technology | Purpose |
|---|---|---|
| Ingestion | Python (yfinance, requests) | Pull prices and financials from external APIs |
| Raw storage | Snowflake VARIANT | Store full API responses for reprocessing |
| Orchestration | Snowflake Streams & Tasks | CDC-based pipeline, no external scheduler |
| Transformation | dbt (dbt-snowflake) | SQL models for silver and gold layers |
| Serving | Streamlit in Snowflake | Dashboard for sector analytics |
| Testing | dbt tests + pytest | Data quality and unit tests |

---

## Snowflake Objects

### Databases
- `comps_bronze` — raw append-only ingestion. Never update rows here.
- `comps_silver` — cleaned, deduplicated, typed. One row per business key.
- `comps_gold` — dbt-built analytics outputs. Business-ready.

### Warehouses
- `ingest_wh` — used by Python ingestion scripts (XSMALL, auto-suspend 60s)
- `transform_wh` — used by Tasks and dbt runs (XSMALL, auto-suspend 60s)

### Role
- `comps_engineer` — all project work runs as this role, never ACCOUNTADMIN

### Key Tables
```
comps_bronze.public.daily_prices          -- raw OHLCV, append-only
comps_bronze.public.company_financials    -- raw quarterly financials, append-only
comps_bronze.public.companies             -- raw company metadata, append-only

comps_silver.public.daily_prices          -- deduped prices, MERGE target
comps_silver.public.company_financials    -- deduped financials, MERGE target
comps_silver.public.companies             -- deduped company master

comps_gold.public.fct_daily_multiples     -- built by dbt, core output
comps_gold.public.agg_sector_multiples    -- built by dbt, sector aggregation
comps_gold.public.agg_sector_dispersion   -- built by dbt, IQR trend
comps_gold.public.dq_alerts               -- data quality monitoring output
```

### Streams (on bronze tables)
```
comps_bronze.public.daily_prices_stream   -- APPEND_ONLY = TRUE
comps_bronze.public.financials_stream     -- APPEND_ONLY = TRUE
comps_bronze.public.companies_stream      -- APPEND_ONLY = TRUE
```

### Tasks
```
comps_bronze.public.transform_prices_task  -- ROOT, runs 6pm ET weekdays
comps_bronze.public.refresh_gold_task      -- CHILD of transform_prices_task
```

Resume order: children before root. Suspend order: root before children.

---

## Ingestion Scripts

```
ingestion/universe.py          -- master list of 100 tickers with GICS sector assignments
ingestion/fetch_prices.py      -- yfinance → comps_bronze.public.daily_prices
ingestion/fetch_financials.py  -- FMP API → comps_bronze.public.company_financials
ingestion/fetch_companies.py   -- FMP API → comps_bronze.public.companies
ingestion/snowflake_loader.py  -- shared connection factory and bulk insert utilities
```

### Running ingestion
```bash
# Historical backfill (run once)
python ingestion/fetch_companies.py
python ingestion/fetch_prices.py --start 2022-01-01
python ingestion/fetch_financials.py

# Daily incremental (run after 4pm ET market close)
python ingestion/fetch_prices.py

# Weekly financial refresh (run Sunday evening)
python ingestion/fetch_financials.py
```

### FMP API rate limit
Free tier: 250 calls/day. Each ticker requires 3 calls for financials (income + balance + cashflow). 100 tickers = 300 calls — split across two days or upgrade to $14/mo Starter plan. Price data uses yfinance (unlimited). Raw responses stored in `_raw VARIANT` column so financials never need to be re-fetched unless the schema changes.

---

## dbt Project

Located in `dbt/`. Target database is `comps_gold`, schema `public`.

### Model DAG
```
stg_prices ──────────────────────────────────────────────────────┐
stg_financials ──► int_prices_with_market_cap ──► fct_daily_multiples ──► agg_sector_multiples
stg_companies ───────────────────────────────────────────────────┘                           └──► agg_sector_dispersion
```

### Materialization strategy
- `staging/` — views (no storage cost, always fresh)
- `intermediate/` — views
- `fct_daily_multiples` — incremental on `(ticker, price_date)`, clustered by `(price_date, gics_sector)`
- `agg_*` — tables (pre-computed for dashboard performance)

### Running dbt
```bash
cd dbt
dbt run                          # build all models
dbt run --select fct_daily_multiples  # build one model
dbt test                         # run all tests
dbt run --full-refresh            # rebuild incrementals from scratch (use after schema changes)
```

### Key business logic in dbt

**TTM financials** — trailing twelve months computed by summing the 4 most recent quarterly periods per ticker. Located in `stg_financials.sql` as a pre-aggregation step.

**Enterprise value** — computed in `int_prices_with_market_cap.sql`:
`EV = (close_price × shares_outstanding) + total_debt - cash`
Uses the most recent quarterly shares/debt/cash data joined to daily prices.

**Outlier filter** — `fct_daily_multiples` excludes `ev_ebitda > 150` and `ev_revenue > 80`. These reflect negative EBITDA (mathematically valid but analytically meaningless for benchmarking). Do not remove this filter without discussion — it exists intentionally.

**IQR** — `agg_sector_multiples` includes `ev_ebitda_iqr = P75 - P25`. This measures within-sector multiple dispersion. A widening IQR over time signals valuation divergence within a sector.

---

## Financial Concepts

Keep these in mind when working on models or explaining the project:

- **EV/EBITDA** — Enterprise Value divided by Earnings Before Interest, Tax, Depreciation, and Amortisation. The most common PE valuation benchmark. Typical ranges: 8-12x for industrials, 15-25x for software, 20-35x for high-growth tech.
- **EV/Revenue** — Enterprise Value divided by annual revenue. Used for high-growth companies where EBITDA may be negative or distorted by investment.
- **P/E** — Price divided by Earnings Per Share. Public market sentiment gauge. Less commonly used in PE than EV multiples.
- **TTM** — Trailing Twelve Months. Sums the last four quarters. Smoother than a single quarter and more representative than annualizing one quarter.
- **GICS** — Global Industry Classification Standard. 11 sectors, 24 industry groups. This project uses GICS sector (top level) and GICS industry (second level) for segmentation.
- **Comps** — Comparable companies analysis. The practice of valuing a target business by reference to publicly traded peers.

---

## Dashboard

`dashboard/app.py` — Streamlit in Snowflake application. Three pages:

1. **Sector Overview** — EV/EBITDA median time series by sector with P25/P75 band shading
2. **Comps Screener** — Filterable table of all 100 companies with current multiples, highlighted vs. sector median
3. **Single Company** — Price history, multiple history vs. sector median, TTM financials summary

Uses `get_active_session()` (Streamlit in Snowflake) not `snowflake.connector.connect()`.
Data is cached with `@st.cache_data(ttl=3600)` — do not remove the cache decorator.

---

## Data Quality

Monitoring runs as a child Task after gold refresh. Results written to `comps_gold.public.dq_alerts`.

```sql
-- Check current status
SELECT * FROM comps_gold.public.dq_alerts
WHERE check_date = CURRENT_DATE
ORDER BY severity, check_name;
```

Active checks: `stale_prices`, `missing_ticker_prices`, `extreme_multiples`, `sector_coverage`.

dbt tests are defined in `dbt/models/**/*.yml`. Run `dbt test` to execute all. All tests must pass before merging to main.

---

## Environment Variables

```env
SNOWFLAKE_ACCOUNT      # format: org-account (e.g. myorg-abc12345)
SNOWFLAKE_USER         # your Snowflake username
SNOWFLAKE_ROLE         # always: comps_engineer
SNOWFLAKE_WAREHOUSE    # ingest_wh for scripts, transform_wh for dbt
SNOWFLAKE_DATABASE     # comps_bronze for ingestion scripts
FMP_API_KEY            # Financial Modeling Prep API key
```

Never commit `.env`. It is in `.gitignore`. Use `.env.example` as the template.

---

## Common Tasks

### Add a new ticker to the universe
1. Add entry to `ingestion/universe.py` with correct GICS sector and industry
2. Run `python ingestion/fetch_companies.py` (loads new company to bronze)
3. Run `python ingestion/fetch_prices.py --tickers NEW_TICKER --start 2022-01-01` (backfill)
4. Run `python ingestion/fetch_financials.py --tickers NEW_TICKER` (load financials)
5. Run `dbt run --full-refresh --select fct_daily_multiples` to include new ticker in gold

### Debug a stale pipeline
```sql
-- Check task history
SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
ORDER BY SCHEDULED_TIME DESC LIMIT 20;

-- Check stream status
SELECT SYSTEM$STREAM_HAS_DATA('comps_bronze.public.daily_prices_stream');

-- Check pipe status (if using Snowpipe)
SELECT SYSTEM$PIPE_STATUS('pipe_name');

-- Check DQ alerts
SELECT * FROM comps_gold.public.dq_alerts WHERE check_date >= CURRENT_DATE - 7;
```

### Force a full gold refresh
```sql
-- Suspend the task first to avoid concurrent runs
ALTER TASK comps_bronze.public.transform_prices_task SUSPEND;
```
```bash
dbt run --full-refresh
```
```sql
-- Resume after dbt completes
ALTER TASK comps_bronze.public.refresh_gold_task RESUME;
ALTER TASK comps_bronze.public.transform_prices_task RESUME;
```

### Check multiple sanity for a specific ticker
```sql
SELECT
  ticker, price_date, close_price,
  market_cap / 1e9 AS market_cap_bn,
  enterprise_value / 1e9 AS ev_bn,
  ev_ebitda, ev_revenue, pe_ratio
FROM comps_gold.public.fct_daily_multiples
WHERE ticker = 'AAPL'
ORDER BY price_date DESC
LIMIT 30;
```

---

## Known Limitations & Gotchas

- **FMP free tier** — 250 calls/day. Financial refreshes for all 100 tickers require 300 calls. Split across two days or upgrade to the Starter plan ($14/mo).
- **yfinance reliability** — occasionally returns empty DataFrames for valid tickers. The ingestion script handles this with a try/except and logs failures. Monitor for persistent gaps.
- **TTM staleness** — if a company hasn't reported earnings in more than 12 months (rare but possible), TTM financials will be understated. The DQ check `missing_recent_quarter` catches this.
- **Stream offset after backfill** — the historical backfill was loaded BEFORE streams were created. Streams only capture rows inserted after their creation. The historical data was loaded directly to silver via manual MERGE. Do not recreate streams unless you intend to lose the offset history.
- **Negative EBITDA** — some tickers may have negative TTM EBITDA (e.g. high-growth unprofitable companies). EV/EBITDA is NULL for these in `fct_daily_multiples` — not 0, not filtered from the table, but excluded from the outlier filter clause. This is correct behavior.
- **Sector coverage for Real Estate and Utilities** — only 5 tickers each. P25/P75 statistics are less meaningful with fewer than 8 observations. Consider expanding these sectors or noting in the dashboard UI that dispersion metrics are approximate.

---

## Coding Conventions

- **Python** — all ingestion scripts use `python-dotenv` for credential loading, `time.sleep(0.3)` between API calls, and explicit error logging per ticker (never silent failures)
- **SQL** — all dbt models use `{{ ref() }}` for model dependencies and `{{ source() }}` for silver sources. Never hardcode database names in dbt SQL.
- **dbt** — staging models are views, mart models are tables or incremental. Always add a model description and column tests to the corresponding `.yml` file when adding a new model.
- **Snowflake** — all DDL uses `CREATE OR REPLACE` for idempotency. Tasks always specify `WAREHOUSE` explicitly. Never run anything as `ACCOUNTADMIN`.
- **Git** — one commit per meaningful milestone. Commit messages follow conventional commits format: `feat:`, `fix:`, `docs:`, `refactor:`. No `wip` or `temp` commits on main.

---

## Architecture Decisions (ADRs)

**Why not Airflow?** Single-platform stack. No external infrastructure to manage. Streams & Tasks provides native CDC that avoids full table scans in the MERGE. Tradeoff: less observability than Airflow's DAG UI.

**Why VARIANT _raw column in bronze?** Insurance policy for reprocessing. If silver transformation logic changes, raw API responses are available in Snowflake without re-calling external APIs. Critical given FMP's free-tier call limits.

**Why incremental dbt on fct_daily_multiples?** Two years × 100 tickers = ~500,000 rows. Full refresh rewrites all rows on every run. Incremental processes only the latest price date — reduces compute from ~60 seconds to ~5 seconds per run.

**Why TTM over most-recent-quarter?** Seasonality. A retailer's Q4 is not representative of annual performance. TTM smooths seasonal variation and is the standard methodology for public comps analysis (matches Bloomberg/FactSet convention).

**Why filter EV/EBITDA > 150x?** Companies with near-zero or negative EBITDA produce extreme or undefined multiples. These are not useful for benchmarking. Filtered at the mart layer so raw data in bronze/silver is preserved.
