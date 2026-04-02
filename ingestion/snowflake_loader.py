"""
Shared Snowflake connection factory and bulk insert utilities for ingestion scripts.

All scripts use python-dotenv to load credentials from .env in the project root.
Connection always uses the comps_engineer role — never ACCOUNTADMIN.
"""

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

# Load .env from project root (one level up from ingestion/)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = logging.getLogger(__name__)


def get_connection(
    warehouse: str | None = None,
    database: str | None = None,
    schema: str = "public",
) -> snowflake.connector.SnowflakeConnection:
    """Return a Snowflake connection using env-var credentials.

    Parameters
    ----------
    warehouse : str, optional
        Override SNOWFLAKE_WAREHOUSE from .env.
    database : str, optional
        Override SNOWFLAKE_DATABASE from .env.
    schema : str
        Schema to use (default: public).
    """

    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        user=os.environ["SNOWFLAKE_USER"],
        warehouse=warehouse or os.environ["SNOWFLAKE_WAREHOUSE"],
        database=database or os.environ["SNOWFLAKE_DATABASE"],
        schema=schema,
    )


def bulk_insert(
    conn: snowflake.connector.SnowflakeConnection,
    table: str,
    rows: list[dict],
    columns: list[str],
    variant_columns: set[str] | None = None,
) -> int:
    """Insert rows into a Snowflake table using executemany.

    Parameters
    ----------
    conn : SnowflakeConnection
        Active connection (database/schema already set).
    table : str
        Fully qualified or short table name.
    rows : list[dict]
        Each dict must contain all keys listed in `columns`.
    columns : list[str]
        Column names in insert order.

    Returns
    -------
    int
        Number of rows inserted.
    """
    if not rows:
        logger.info("No rows to insert into %s — skipping.", table)
        return 0

    variant_columns = variant_columns or set()
    col_list = ", ".join(columns)
    placeholders = ", ".join(
        "PARSE_JSON(%s)" if c in variant_columns else "%s"
        for c in columns
    )
    sql = f"INSERT INTO {table} ({col_list}) SELECT {placeholders}"

    cur = conn.cursor()
    try:
        for row in rows:
            vals = list(row.values())
            cur.execute(sql, vals)
        logger.info("Inserted %d rows into %s.", len(rows), table)
        return len(rows)
    finally:
        cur.close()


def to_variant(obj: dict | list | None) -> str | None:
    """Serialize a Python object to a JSON string for Snowflake VARIANT columns."""
    if obj is None:
        return None
    return json.dumps(obj)


def utcnow_iso() -> str:
    """Return current UTC timestamp as ISO-8601 string."""
    return datetime.now()
