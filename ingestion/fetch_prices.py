"""
Fetch daily OHLCV price data from yfinance and load into
comps_bronze.public.daily_prices.

Usage
-----
    # Historical backfill (2 years)
    python -m ingestion.fetch_prices --start 2024-04-01

    # Specific tickers with custom range
    python -m ingestion.fetch_prices --tickers AAPL MSFT --start 2024-01-01

    # Daily incremental (last 5 trading days)
    python -m ingestion.fetch_prices

    # Export to CSV instead of loading to Snowflake
    python -m ingestion.fetch_prices --start 2024-04-01 --csv
    python -m ingestion.fetch_prices --start 2024-04-01 --csv data/custom_name.csv
"""

import argparse
import csv
import logging
import os
import time
from datetime import date, timedelta

import yfinance as yf

from ingestion.snowflake_loader import get_connection
from ingestion.universe import TICKERS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

DDL = """\
CREATE TABLE IF NOT EXISTS comps_bronze.public.daily_prices (
  ingested_at   TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP,
  source        VARCHAR,
  ticker        VARCHAR,
  price_date    DATE,
  open          FLOAT,
  high          FLOAT,
  low           FLOAT,
  close         FLOAT,
  adj_close     FLOAT,
  volume        BIGINT,
  _raw          VARIANT
);
"""

INSERT_SQL = """\
INSERT INTO comps_bronze.public.daily_prices
  (source, ticker, price_date, open, high, low, close, adj_close, volume, _raw)
SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s, PARSE_JSON(%s)
"""


def fetch_rows(ticker: str, start: str, end: str) -> list[tuple]:
    """Fetch price history for one ticker. Returns list of row tuples."""
    try:
        df = yf.download(ticker, start=start, end=end, auto_adjust=False, progress=False, multi_level_index=False)
    except Exception as exc:
        logger.error("yfinance download failed for %s: %s", ticker, exc)
        return []

    if df.empty:
        logger.warning("No data returned for %s", ticker)
        return []

    df.reset_index(inplace=True)
    rows = []
    for _, row in df.iterrows():
        rows.append((
            "yfinance",
            ticker,
            str(row["Date"]),
            float(row["Open"]),
            float(row["High"]),
            float(row["Low"]),
            float(row["Close"]),
            float(row["Adj Close"]),
            int(row["Volume"]),
            row.to_json(),
        ))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch daily prices from yfinance → bronze")
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=None,
        help="Specific tickers to fetch (default: all in universe)",
    )
    parser.add_argument(
        "--start",
        default=None,
        help="Start date YYYY-MM-DD (default: 5 trading days ago for incremental)",
    )
    parser.add_argument(
        "--end",
        default=None,
        help="End date YYYY-MM-DD (default: today)",
    )
    parser.add_argument(
        "--csv",
        nargs="?",
        const="data/daily_prices.csv",
        default=None,
        help="Write to CSV instead of Snowflake (default path: data/daily_prices.csv)",
    )
    args = parser.parse_args()

    tickers = args.tickers if args.tickers else TICKERS
    end = args.end or str(date.today())
    start = args.start or str(date.today() - timedelta(days=7))

    logger.info(
        "Fetching prices for %d tickers from %s to %s.", len(tickers), start, end
    )

    # Fetch all tickers
    total_rows = 0
    failed = []
    all_rows = []
    for i, ticker in enumerate(tickers, 1):
        logger.info("[%d/%d] Fetching %s", i, len(tickers), ticker)
        rows = fetch_rows(ticker, start, end)
        if rows:
            all_rows.extend(rows)
            total_rows += len(rows)
            logger.info("  → %d rows for %s", len(rows), ticker)
        else:
            failed.append(ticker)
        time.sleep(0.3)

    if failed:
        logger.warning("Failed tickers (%d): %s", len(failed), ", ".join(failed))

    if not all_rows:
        logger.warning("No data fetched — exiting.")
        return

    if args.csv:
        # Write to CSV
        csv_path = args.csv
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)
        header = ["source", "ticker", "price_date", "open", "high", "low",
                  "close", "adj_close", "volume", "_raw"]
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f, delimiter="|")
            writer.writerow(header)
            writer.writerows(all_rows)
        logger.info("Done. Wrote %d rows to %s", total_rows, csv_path)
    else:
        # Load directly into Snowflake
        conn = get_connection(database="comps_bronze")
        cursor = conn.cursor()
        try:
            cursor.execute(DDL)
            logger.info("Ensured daily_prices table exists.")
            for row in all_rows:
                cursor.execute(INSERT_SQL, row)
            logger.info("Done. Loaded %d total price rows into bronze.", total_rows)
        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    main()
