"""
Fetch company profile data from Financial Modeling Prep (FMP) and load into
comps_bronze.public.companies.

Usage
-----
    # Load all tickers in the universe
    python -m ingestion.fetch_companies

    # Load specific tickers only
    python -m ingestion.fetch_companies --tickers AAPL MSFT NVDA

The raw FMP JSON response is stored in a VARIANT column (_raw) so financials
never need to be re-fetched unless the schema changes.
"""

import argparse
import logging
import os
import sys
import time

import requests

from ingestion.snowflake_loader import (
    bulk_insert,
    get_connection,
    to_variant,
    utcnow_iso,
)
from ingestion.universe import TICKERS, UNIVERSE

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

FMP_BASE_URL = "https://financialmodelingprep.com/stable"

# Bronze table DDL — executed once per run (idempotent CREATE OR REPLACE is
# avoided here to prevent dropping existing data; CREATE IF NOT EXISTS is safe).
DDL = """\
CREATE TABLE IF NOT EXISTS comps_bronze.public.companies (
  ingested_at       TIMESTAMP_TZ DEFAULT CURRENT_TIMESTAMP,
  ticker            VARCHAR,
  company_name      VARCHAR,
  gics_sector       VARCHAR,
  gics_industry     VARCHAR,
  exchange          VARCHAR,
  _raw              VARIANT
);
"""

COLUMNS = [
    "ingested_at",
    "ticker",
    "company_name",
    "gics_sector",
    "gics_industry",
    "exchange",    
    "_raw",
]


def fetch_profile(ticker: str, api_key: str) -> dict | None:
    """Fetch a single company profile from FMP. Returns the raw dict or None."""
    url = f"{FMP_BASE_URL}/search-symbol"
    try:
        resp = requests.get(url, params={"query": ticker, "apikey": api_key}, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            return data[0]
        logger.warning("Empty response for %s", ticker)
        return None
    except requests.RequestException as exc:
        logger.error("Failed to fetch %s: %s", ticker, exc)
        return None


def _lookup_universe(ticker: str) -> dict | None:
    """Find a ticker's entry in the local universe for GICS overrides."""
    for entry in UNIVERSE:
        if entry["ticker"] == ticker:
            return entry
    return None


def transform_profile(raw: dict, ticker: str) -> dict:
    """Map raw FMP profile to bronze row.

    GICS sector and industry come from our curated universe.py rather than
    FMP's sector/industry fields, which can be inconsistent.
    """
    universe_entry = _lookup_universe(ticker)
    return {
        "ingest_at": utcnow_iso(),
        "ticker": ticker,
        "company_name": raw.get("name"),
        "gics_sector": universe_entry["gics_sector"] if universe_entry else raw.get("sector"),
        "gics_industry": universe_entry["gics_industry"] if universe_entry else raw.get("industry"),                        
        "exchange": raw.get("exchange"),
        "_raw": to_variant(raw)        
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch company profiles from FMP → bronze")
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=None,
        help="Specific tickers to fetch (default: all in universe)",
    )
    args = parser.parse_args()

    api_key = os.environ.get("FMP_API_KEY")
    if not api_key:
        logger.error("FMP_API_KEY not set. Check your .env file.")
        sys.exit(1)

    tickers = args.tickers if args.tickers else TICKERS
    logger.info("Fetching company profiles for %d tickers.", len(tickers))

    # Fetch from FMP
    rows: list[dict] = []
    failed: list[str] = []
    for i, ticker in enumerate(tickers, 1):
        logger.info("[%d/%d] Fetching %s", i, len(tickers), ticker)
        raw = fetch_profile(ticker, api_key)
        if raw:
            rows.append(transform_profile(raw, ticker))
        else:
            failed.append(ticker)
        time.sleep(0.3)  # rate-limit courtesy

    logger.info(
        "Fetched %d profiles successfully, %d failed.", len(rows), len(failed)
    )
    if failed:
        logger.warning("Failed tickers: %s", ", ".join(failed))

    if not rows:
        logger.warning("No data to load — exiting.")
        sys.exit(0)

    # Load into Snowflake
    conn = get_connection(database="comps_bronze")    
    try:
        cur = conn.cursor()
        cur.execute(DDL)
        cur.close()
        logger.info("Ensured companies table exists.")        
        inserted = bulk_insert(conn, "comps_bronze.public.companies", rows, COLUMNS, variant_columns={"_raw"})
        logger.info("Done. Loaded %d company records into bronze.", inserted)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
