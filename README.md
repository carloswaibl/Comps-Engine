# PE Public Comps Engine

An automated public comparable company benchmarking platform that ingests daily pricing and quarterly financial data for 100 S&P 500 equities, computes trailing valuation multiples, and surfaces sector-level analytics via a Streamlit dashboard — all within a Snowflake medallion architecture.

---

## What This Is

Private equity deal teams benchmark portfolio companies against public market comparables constantly. Analysts manually pull price data, look up EV/EBITDA multiples, and track how sector valuations are moving — often in Excel, updated weekly at best.

This project automates that workflow end-to-end. Every trading day, fresh price data is ingested, trailing twelve month (TTM) financials are joined to compute valuation multiples, and sector-level statistics (median, P25, P75) are updated and made available in a live dashboard. What would take an analyst several hours per week runs automatically and is always current.

**Valuation multiples computed:**
- EV/EBITDA — enterprise value relative to operating earnings (the most common PE benchmark)
- EV/Revenue — enterprise value relative to top-line revenue (key for high-growth companies)
- P/E — price-to-earnings (public market sentiment indicator)
- 30/60/90-day price return — trailing performance by ticker and sector

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Data Sources                           │
│   yfinance (daily prices)    FMP free tier (financials)     │
└────────────────────┬────────────────────────────────────────┘
                     │ Python ingestion scripts
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  BRONZE  comps_bronze.public                                │
│  Append-only raw ingestion. Never modified.                 │
│  daily_prices │ company_financials │ companies              │
│  All raw API responses stored in VARIANT (_raw column)      │
└────────────────────┬────────────────────────────────────────┘
                     │ Snowflake Streams + Tasks (MERGE)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  SILVER  comps_silver.public                                │
│  Cleaned, deduplicated, typed. One row per business key.    │
│  daily_prices │ company_financials │ companies              │
│  Enterprise value computed here (mkt_cap + debt - cash)     │
└────────────────────┬────────────────────────────────────────┘
                     │ dbt (incremental models)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  GOLD  comps_gold.public                                    │
│  Business-ready. PE analytics outputs.                      │
│  fct_daily_multiples   — ticker × date × multiples          │
│  agg_sector_multiples  — sector medians + IQR daily         │
│  agg_sector_dispersion — multiple spread over time          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
          Streamlit in Snowflake Dashboard
```

### Why This Architecture

**Medallion layers** enforce a clean separation between raw data (bronze), reliable data (silver), and analytics-ready data (gold). If a transformation bug is introduced, bronze is untouched — the pipeline can be replayed from source without re-calling any APIs.

**Snowflake Streams & Tasks** for orchestration rather than an external tool like Airflow keeps the entire stack within Snowflake. Streams provide native CDC — the silver MERGE only processes rows that are genuinely new in bronze, not full table scans. Tasks fire automatically on market close with no external scheduler to maintain.

**dbt for the gold layer** separates transformation logic from orchestration. Each model is independently testable, version-controlled, and incrementally materialized — only new price dates are processed on each run rather than recomputing the full two-year history.

**Incremental dbt models** on `fct_daily_multiples` mean the gold layer processes only the latest price date on each daily run. Full refreshes are triggered only when schema changes require it.

---

## Equity Universe

100 S&P 500 constituents across all 11 GICS sectors, selected to provide sufficient depth per sector for meaningful statistical aggregation (8-10 names minimum per sector).

| GICS Sector | Names | Example tickers |
|---|---|---|
| Information Technology | 14 | AAPL, MSFT, NVDA, CRM, ADBE |
| Health Care | 12 | UNH, JNJ, LLY, ABBV, MRK |
| Financials | 11 | JPM, BAC, GS, MS, BLK |
| Consumer Discretionary | 10 | AMZN, TSLA, HD, MCD, NKE |
| Communication Services | 9 | GOOGL, META, NFLX, DIS, T |
| Industrials | 10 | HON, UPS, CAT, DE, RTX |
| Consumer Staples | 9 | PG, KO, PEP, WMT, COST |
| Energy | 8 | CVX, XOM, COP, EOG, SLB |
| Materials | 7 | LIN, APD, FCX, NEM, DD |
| Utilities | 5 | NEE, DUK, SO, AEP, EXC |
| Real Estate | 5 | AMT, PLD, EQIX, SPG, PSA |

---

## Key dbt Models

### `fct_daily_multiples`
The core PE analytics fact table. One row per ticker per trading day. Joins daily prices to trailing twelve month (TTM) financials — summing the four most recent quarterly periods — and computes all three valuation multiples. Materialized incrementally on `(ticker, price_date)`.

TTM methodology: sum the four most recent quarterly `revenue`, `ebitda`, and `net_income` values per ticker. Enterprise value is recomputed daily using the current close price × latest shares outstanding + net debt.

Outlier filter: rows where `ev_ebitda > 150` or `ev_revenue > 80` are excluded from the mart — these reflect negative EBITDA or data errors, not real multiples.

### `agg_sector_multiples`
Daily sector-level aggregation of `fct_daily_multiples`. Computes median, 25th percentile, and 75th percentile for EV/EBITDA and EV/Revenue per sector per day. The IQR (P75 - P25) measures within-sector multiple dispersion — a widening IQR signals increasing valuation divergence within a sector, which PE investors track as a deal timing signal.

### `agg_sector_dispersion`
Tracks how sector IQR has moved over the trailing 12 months. Used in the dashboard to show whether sector valuations are compressing (converging) or expanding (diverging).

---

## Data Sources

### yfinance
Open-source Python library wrapping Yahoo Finance. Used for all daily OHLCV price data. No API key required. Rate limits are generous for a 100-ticker universe with staggered requests.

### Financial Modeling Prep (FMP)
Used for quarterly income statement, balance sheet, and cash flow data. Free tier provides 250 API calls per day — sufficient for weekly financial refreshes on 100 tickers when batched intelligently (3 calls per ticker × 100 tickers = 300 calls; split across two days or upgrade to the $14/month Starter plan).

FMP endpoints used:
- `/income-statement/{ticker}?period=quarter&limit=12`
- `/balance-sheet-statement/{ticker}?period=quarter&limit=12`
- `/cash-flow-statement/{ticker}?period=quarter&limit=12`

All raw API responses are stored in the `_raw VARIANT` column in bronze tables. This means financials can be reprocessed from bronze without re-calling the API — important for free-tier users managing call limits.

---

## Setup

### Prerequisites
- Python 3.11+
- Snowflake account (free 30-day trial at snowflake.com)
- FMP API key (free at financialmodelingprep.com)
- dbt-snowflake (`pip install dbt-snowflake`)

### 1. Clone and install dependencies

```bash
git clone https://github.com/yourusername/pe-comps-engine.git
cd pe-comps-engine
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
# Edit .env with your Snowflake account details and FMP API key
```

```env
SNOWFLAKE_ACCOUNT=your_org-your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_ROLE=comps_engineer
SNOWFLAKE_WAREHOUSE=ingest_wh
SNOWFLAKE_DATABASE=comps_bronze
FMP_API_KEY=your_fmp_key
```

### 3. Set up Snowflake infrastructure

```bash
# Run DDL in order
snowsql -f snowflake/01_bronze_ddl.sql
snowsql -f snowflake/02_silver_ddl.sql
snowsql -f snowflake/03_gold_ddl.sql
snowsql -f snowflake/04_streams_tasks.sql
snowsql -f snowflake/05_stored_procedures.sql
```

Or paste each file into a Snowflake worksheet and run manually.

### 4. Run initial historical backfill

```bash
# Load 2 years of price history for all 100 tickers (~50,000 rows)
python ingestion/fetch_companies.py
python ingestion/fetch_prices.py --start 2022-01-01
python ingestion/fetch_financials.py  # May need to split across two days on FMP free tier
```

Expected runtime: 10-15 minutes for full backfill.

### 5. Initialize and run dbt

```bash
cd dbt
dbt debug          # verify connection
dbt run            # build all models
dbt test           # run data quality tests
```

### 6. Activate the pipeline

```bash
# Resume Tasks in the correct order (children before root)
snowsql -q "ALTER TASK comps_bronze.public.refresh_gold_task RESUME;"
snowsql -q "ALTER TASK comps_bronze.public.transform_prices_task RESUME;"
```

The root task fires at 6:00 PM ET on weekdays — after US market close. Daily price ingestion should be scheduled to run before this (e.g. 5:30 PM ET via cron or a scheduled Python job).

### 7. Deploy the dashboard

Upload `dashboard/app.py` to Streamlit in Snowflake:

```
Snowsight → Streamlit → + Streamlit App → upload app.py
```

---

## Running Daily Ingestion

The ingestion scripts are designed to be idempotent — running them multiple times on the same day will not create duplicate rows in silver (the MERGE handles deduplication).

```bash
# Daily price update (run after 4 PM ET market close)
python ingestion/fetch_prices.py

# Weekly financial refresh (run Sunday evening or Monday morning)
python ingestion/fetch_financials.py
```

Schedule these with cron, a Cloud Function, or a GitHub Actions workflow.

---

## Data Quality Monitoring

A daily monitoring Task writes to `comps_gold.public.dq_alerts` when checks fail. Query this table to see current data quality status:

```sql
SELECT * FROM comps_gold.public.dq_alerts
WHERE check_date = CURRENT_DATE
ORDER BY severity, check_name;
```

Checks run daily:
- **stale_prices** — flags if max price date is more than 2 days old
- **missing_ticker_prices** — identifies tickers with no data in the last 5 trading days
- **extreme_multiples** — flags EV/EBITDA > 150x (indicates negative EBITDA or data error)
- **sector_coverage** — verifies all 11 GICS sectors have data for the current date

---

## Project Structure

```
pe-comps-engine/
├── README.md
├── CLAUDE.md                       # AI assistant context for this project
├── .env.example
├── .gitignore
├── requirements.txt
├── ingestion/
│   ├── __init__.py
│   ├── universe.py                 # 100-ticker universe with GICS sector tags
│   ├── fetch_prices.py             # yfinance daily price loader
│   ├── fetch_financials.py         # FMP quarterly financials loader
│   ├── fetch_companies.py          # Company metadata loader
│   └── snowflake_loader.py         # Shared connection and bulk load utilities
├── snowflake/
│   ├── 01_bronze_ddl.sql
│   ├── 02_silver_ddl.sql
│   ├── 03_gold_ddl.sql
│   ├── 04_streams_tasks.sql
│   └── 05_stored_procedures.sql
├── dbt/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── staging/
│   │   │   ├── stg_prices.sql
│   │   │   ├── stg_financials.sql
│   │   │   └── stg_companies.sql
│   │   ├── intermediate/
│   │   │   └── int_prices_with_market_cap.sql
│   │   └── marts/
│   │       ├── fct_daily_multiples.sql
│   │       ├── agg_sector_multiples.sql
│   │       └── agg_sector_dispersion.sql
│   └── tests/
│       └── generic/
├── dashboard/
│   └── app.py                      # Streamlit in Snowflake application
└── tests/
    ├── test_data_quality.py
    └── test_multiples.py
```

---

## Design Decisions

**Why TTM financials instead of the most recent quarter?**
Trailing twelve months smooths seasonal variation. A retailer's Q4 EBITDA is not representative of its annual earnings power. TTM gives a more comparable cross-sector view — the same methodology used by Bloomberg and FactSet for public comps.

**Why store raw API responses in a VARIANT column?**
The bronze `_raw` column is an insurance policy. If a silver transformation bug corrupts data, or if financial statement line items are mapped incorrectly, the original API response is available in Snowflake for reprocessing without re-calling the API. Especially important on FMP's free tier where re-fetching 100 tickers costs 300 API calls.

**Why Snowflake Streams & Tasks instead of Airflow?**
For a single-platform stack, Streams & Tasks eliminates external infrastructure. Streams provide native CDC — only genuinely new bronze rows flow through the MERGE, no full table scans. The tradeoff is less observability than Airflow's DAG UI. For a multi-system pipeline involving external databases or APIs, Airflow would be the right choice.

**Why incremental dbt models?**
`fct_daily_multiples` covers two years of history across 100 tickers — roughly 500,000 rows. A full refresh on every run would recompute all rows daily. Incrementally materializing on `(ticker, price_date)` processes only the latest price date on each run, reducing compute time from minutes to seconds.

**Why exclude EV/EBITDA > 150x?**
Extreme multiples almost always indicate negative or near-zero EBITDA — mathematically valid but analytically meaningless for benchmarking. A company with -$10M EBITDA trading at $5B EV technically has a -500x multiple. These are filtered at the mart layer rather than silver so the underlying data is preserved.

---

## What's Next

- **Forward estimates layer** — incorporate consensus forward EV/EBITDA using FactSet or Bloomberg API for prospective multiple analysis, which is more relevant for deal teams than trailing
- **Valuation alert system** — surface when a company's multiple compresses or expands more than one standard deviation week-over-week, a signal worth flagging for deal monitoring
- **Deal announcement enrichment** — join announced M&A transactions to reconstruct target trading multiples at announcement, enabling precedent transaction analysis
- **Peer group customization** — allow users to define custom comp sets beyond the static GICS universe, mirroring how PE analysts build bespoke comps for specific deals

---

## License

MIT
