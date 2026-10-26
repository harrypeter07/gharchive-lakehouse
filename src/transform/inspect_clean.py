"""Inspect clean Parquet layer metrics using DuckDB."""

import duckdb
from src.common.config import CLEAN_DATA_DIR


def inspect_clean_dataset() -> None:
    con = duckdb.connect()
    parquet_pattern = str(CLEAN_DATA_DIR / "*" / "*" / "*.parquet").replace("\\", "/")

    query = f"""
        SELECT 
            event_type, 
            count(*) as count, 
            count(distinct repo_id) as unique_repos, 
            count(distinct actor_hash) as unique_actors
        FROM read_parquet('{parquet_pattern}')
        GROUP BY event_type
        ORDER BY count DESC
    """
    rows = con.execute(query).fetchall()

    print("\n" + "=" * 70)
    print("CLEAN LAYER (PARQUET) SUMMARY METRICS (DUCKDB)")
    print("=" * 70)
    print(f"{'Event Type':<25} {'Total Rows':>12} {'Unique Repos':>15} {'Unique Actors':>15}")
    print("-" * 70)
    total_rows = 0
    for r in rows:
        total_rows += r[1]
        print(f"{r[0]:<25} {r[1]:>12,} {r[2]:>15,} {r[3]:>15,}")
    print("-" * 70)
    print(f"{'TOTAL KEPT ROWS':<25} {total_rows:>12,}")
    print("=" * 70)


if __name__ == "__main__":
    inspect_clean_dataset()
