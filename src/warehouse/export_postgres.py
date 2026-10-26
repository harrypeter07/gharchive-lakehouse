"""Export curated DuckDB Star Schema tables directly into PostgreSQL.

Synchronizes fact, dimension, and aggregated tables from data/lakehouse.duckdb
into the PostgreSQL serving warehouse for Metabase BI dashboards.
"""

import os
from pathlib import Path
from typing import Dict, Any, List
import duckdb

from src.common.config import PROJECT_ROOT


def export_to_postgres(
    db_path: Path | None = None,
    pg_host: str = "localhost",
    pg_port: int = 5432,
    pg_user: str | None = None,
    pg_password: str | None = None,
    pg_database: str | None = None,
) -> Dict[str, Any]:
    """Attach to PostgreSQL and copy curated tables from DuckDB."""
    if db_path is None:
        db_path = PROJECT_ROOT / "data" / "lakehouse.duckdb"

    pg_user = pg_user or os.getenv("POSTGRES_USER", "lakehouse_user")
    pg_password = pg_password or os.getenv("POSTGRES_PASSWORD", "lakehouse_secure_password")
    pg_database = pg_database or os.getenv("POSTGRES_DB", "lakehouse_db")

    con = duckdb.connect(str(db_path))

    # Install and load DuckDB's postgres extension
    con.execute("INSTALL postgres;")
    con.execute("LOAD postgres;")

    conn_str = f"host={pg_host} port={pg_port} user={pg_user} password={pg_password} dbname={pg_database}"
    con.execute(f"ATTACH '{conn_str}' AS pg (TYPE postgres);")

    tables_to_export = [
        "dim_date",
        "dim_event_type",
        "dim_repo",
        "dim_actor",
        "agg_stars_per_repo_day",
        "agg_events_per_hour",
        "fact_events",
    ]

    exported_stats: Dict[str, int] = {}
    for tbl in tables_to_export:
        con.execute(f"CREATE TABLE IF NOT EXISTS pg.{tbl} AS SELECT * FROM {tbl} LIMIT 0;")
        # Truncate and insert for idempotency
        con.execute(f"DELETE FROM pg.{tbl};")
        con.execute(f"INSERT INTO pg.{tbl} SELECT * FROM {tbl};")
        count = con.execute(f"SELECT count(*) FROM pg.{tbl};").fetchone()[0]
        exported_stats[tbl] = count

    con.execute("DETACH pg;")
    con.close()

    return {"status": "success", "tables": exported_stats}


if __name__ == "__main__":
    res = export_to_postgres()
    print(f"Export to PostgreSQL complete: {res}")
