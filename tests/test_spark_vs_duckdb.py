"""Cross-engine reconciliation test comparing PySpark aggregations against DuckDB."""

from pathlib import Path
import pytest
import duckdb

pyspark = pytest.importorskip("pyspark", reason="PySpark is required for cross-engine tests")
from src.spark.agg_job import run_spark_aggregations
from src.common.config import PROJECT_ROOT


def test_spark_vs_duckdb_reconciliation():
    db_path = PROJECT_ROOT / "data" / "lakehouse.duckdb"
    assert db_path.exists(), "Lakehouse DuckDB database must exist"

    # 1. Fetch DuckDB aggregations directly on clean Parquet layer
    con = duckdb.connect(str(db_path), read_only=True)
    duck_raw_stars_rows = con.execute("""
        SELECT repo_name, COUNT(*) AS star_count
        FROM read_parquet('data/clean/*/*/*.parquet')
        WHERE event_type = 'WatchEvent' AND action = 'started'
        GROUP BY repo_name
    """).fetchall()
    duck_stars = {r[0]: r[1] for r in duck_raw_stars_rows}

    duck_hourly_rows = con.execute("""
        SELECT hour, event_type, event_count
        FROM agg_events_per_hour
    """).fetchall()
    duck_hourly = {(int(r[0]), str(r[1])): int(r[2]) for r in duck_hourly_rows}
    con.close()

    # 2. Run PySpark aggregations
    spark_stars, spark_hourly = run_spark_aggregations()

    # 3. Assert mathematical equality between engines
    assert len(spark_stars) == len(duck_stars), f"Star count mismatch: Spark {len(spark_stars)} vs DuckDB {len(duck_stars)}"
    assert len(spark_hourly) == len(duck_hourly), f"Hourly bins mismatch: Spark {len(spark_hourly)} vs DuckDB {len(duck_hourly)}"

    # Check all hourly bins match exactly
    for key, count in duck_hourly.items():
        assert spark_hourly.get(key) == count, f"Mismatch at {key}: Spark {spark_hourly.get(key)} != DuckDB {count}"

    # Verify all top 100 starred repos match exactly across engines
    top_duck_repos = sorted(duck_stars.items(), key=lambda x: x[1], reverse=True)[:100]
    for repo, count in top_duck_repos:
        assert spark_stars.get(repo) == count, f"Star mismatch for {repo}: Spark {spark_stars.get(repo)} != DuckDB {count}"
