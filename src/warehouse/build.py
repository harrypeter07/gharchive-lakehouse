"""Build curated star schema inside DuckDB and verify integrity constraints.

Executes build_star.sql against clean Parquet data, creates tables inside
data/lakehouse.duckdb, and runs referential integrity and count checks.
"""

import logging
from pathlib import Path
from typing import Any, Dict

import duckdb

from src.common.config import CLEAN_DATA_DIR, DATA_DIR, PROJECT_ROOT

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_PATH = DATA_DIR / "lakehouse.duckdb"
SQL_PATH = PROJECT_ROOT / "src" / "warehouse" / "build_star.sql"


def build_star_schema(db_path: Path = DB_PATH, sql_path: Path = SQL_PATH) -> Dict[str, Any]:
    """Execute DDL build script and return table metrics."""
    logger.info("Opening DuckDB connection at %s ...", db_path)
    con = duckdb.connect(str(db_path))

    with open(sql_path, "r", encoding="utf-8") as f:
        sql_commands = f.read()

    logger.info("Executing build_star.sql ...")
    # Execute DDL statements
    con.execute(sql_commands)
    logger.info("Star schema tables created successfully.")

    # 1. Row counts
    fact_count = con.execute("SELECT count(*) FROM fact_events").fetchone()[0]
    repo_count = con.execute("SELECT count(*) FROM dim_repo").fetchone()[0]
    actor_count = con.execute("SELECT count(*) FROM dim_actor").fetchone()[0]
    type_count = con.execute("SELECT count(*) FROM dim_event_type").fetchone()[0]
    date_count = con.execute("SELECT count(*) FROM dim_date").fetchone()[0]
    agg_stars = con.execute("SELECT count(*) FROM agg_stars_per_repo_day").fetchone()[0]
    agg_hourly = con.execute("SELECT count(*) FROM agg_events_per_hour").fetchone()[0]

    # Verify against clean Parquet row count
    parquet_pattern = str(CLEAN_DATA_DIR / "*" / "*" / "*.parquet").replace("\\", "/")
    parquet_count = con.execute(f"SELECT count(*) FROM read_parquet('{parquet_pattern}')").fetchone()[0]

    logger.info("Parquet rows: %d | Fact rows: %d", parquet_count, fact_count)
    if fact_count != parquet_count:
        raise AssertionError(f"Count mismatch: fact_events has {fact_count} rows, Parquet has {parquet_count}")

    # 2. Check for duplicate keys in fact_events
    unique_keys = con.execute("SELECT count(DISTINCT event_id) FROM fact_events").fetchone()[0]
    if unique_keys != fact_count:
        raise AssertionError(f"Duplicate keys found in fact_events: {fact_count - unique_keys} duplicates")

    # 3. Check for orphan foreign keys
    orphan_events = con.execute("""
        SELECT count(*) FROM fact_events 
        WHERE repo_key IS NULL 
           OR actor_key IS NULL 
           OR event_type_key IS NULL 
           OR date_key IS NULL
    """).fetchone()[0]
    if orphan_events > 0:
        raise AssertionError(f"Found {orphan_events} orphan foreign keys in fact_events!")

    logger.info("All referential integrity and reconciliation checks passed!")
    con.close()

    return {
        "fact_events": fact_count,
        "dim_repo": repo_count,
        "dim_actor": actor_count,
        "dim_event_type": type_count,
        "dim_date": date_count,
        "agg_stars_per_repo_day": agg_stars,
        "agg_events_per_hour": agg_hourly,
        "orphan_keys": orphan_events,
    }


if __name__ == "__main__":
    metrics = build_star_schema()
    print("\n" + "=" * 60)
    print("DUCKDB STAR SCHEMA BUILD COMPLETE")
    print("=" * 60)
    for table_name, count in metrics.items():
        print(f"  {table_name:<28}: {count:>12,}")
    print("=" * 60)
