import duckdb
from pathlib import Path

full_db = Path("data/lakehouse.duckdb")
demo_db = Path("data/curated/demo_lakehouse.duckdb")

if full_db.exists():
    if demo_db.exists():
        demo_db.unlink()
    con = duckdb.connect(str(demo_db))
    con.execute(f"ATTACH '{full_db.as_posix()}' AS src (READ_ONLY)")
    
    con.execute("CREATE TABLE dim_date AS SELECT * FROM src.dim_date")
    con.execute("CREATE TABLE dim_event_type AS SELECT * FROM src.dim_event_type")
    con.execute("CREATE TABLE agg_stars_per_repo_day AS SELECT * FROM src.agg_stars_per_repo_day")
    con.execute("CREATE TABLE agg_events_per_hour AS SELECT * FROM src.agg_events_per_hour")
    con.execute("CREATE TABLE dim_repo AS SELECT * FROM src.dim_repo LIMIT 25000")
    con.execute("CREATE TABLE dim_actor AS SELECT * FROM src.dim_actor LIMIT 25000")
    con.execute("CREATE TABLE fact_events AS SELECT * FROM src.fact_events LIMIT 50000")
    
    con.close()
    print("Demo DuckDB created successfully. Size:", demo_db.stat().st_size)
else:
    print("Full DB not found")
