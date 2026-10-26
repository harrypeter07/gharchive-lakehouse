"""PySpark aggregation pipeline for cross-engine reconciliation with DuckDB.

Reads clean partitioned Parquet files using Apache Spark SQL,
computes daily repository stars and hourly event distributions,
and validates distributed calculations against DuckDB analytical aggregates.
"""

from pathlib import Path
from typing import Dict, Any, Tuple
import os

from src.common.config import CLEAN_DATA_DIR, PROJECT_ROOT


def run_spark_aggregations(clean_dir: Path | None = None) -> Tuple[Dict[str, int], Dict[Tuple[int, str], int]]:
    """Compute stars per repo and events per hour using local PySpark in UTC."""
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import col, count, hour

    if clean_dir is None:
        clean_dir = CLEAN_DATA_DIR / "event_date=2024-06-10"

    # Configure local standalone Spark driver pinned explicitly to UTC
    spark = (
        SparkSession.builder
        .appName("GHArchive-CrossEngine-Reconciliation")
        .master("local[2]")
        .config("spark.driver.memory", "2g")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.sql.session.timeZone", "UTC")
        .getOrCreate()
    )

    # Reading base directory allows Spark to automatically infer the partition column 'event_type'
    df = spark.read.parquet(str(clean_dir))

    # 1. Stars per repo: WatchEvent with action='started'
    stars_df = (
        df.filter((col("event_type") == "WatchEvent") & (col("action") == "started"))
        .groupBy("repo_name")
        .agg(count("*").alias("star_count"))
    )
    stars_rows = stars_df.collect()
    spark_stars = {r["repo_name"]: r["star_count"] for r in stars_rows}

    # 2. Events per hour in UTC: group by hour extracted from created_at, event_type
    df_with_hour = df.withColumn("hour", hour(col("created_at")))
    hourly_df = (
        df_with_hour.groupBy("hour", "event_type")
        .agg(count("*").alias("event_count"))
    )
    hourly_rows = hourly_df.collect()
    spark_hourly = {(int(r["hour"]), str(r["event_type"])): int(r["event_count"]) for r in hourly_rows}

    spark.stop()
    return spark_stars, spark_hourly


if __name__ == "__main__":
    stars, hourly = run_spark_aggregations()
    print(f"PySpark Aggregation Complete: {len(stars)} repos with stars, {len(hourly)} hourly bins.")
