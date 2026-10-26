"""Unit tests for the DuckDB curated star schema data warehouse."""

from pathlib import Path
import duckdb
import pytest

from src.common.config import DATA_DIR, PROJECT_ROOT

DB_PATH = DATA_DIR / "lakehouse.duckdb"
AGENT_QUERIES_PATH = PROJECT_ROOT / "sql" / "agent_queries.sql"
MY_QUERIES_PATH = PROJECT_ROOT / "sql" / "my_queries.sql"


def test_star_schema_tables_and_row_counts() -> None:
    """Verify that all warehouse tables exist with populated data."""
    assert DB_PATH.exists(), f"Database missing at {DB_PATH}"
    con = duckdb.connect(str(DB_PATH), read_only=True)

    expected_tables = {
        "fact_events",
        "dim_repo",
        "dim_actor",
        "dim_event_type",
        "dim_date",
        "agg_stars_per_repo_day",
        "agg_events_per_hour",
    }
    existing_tables = set(r[0] for r in con.execute("SHOW TABLES").fetchall())
    assert expected_tables.issubset(existing_tables), f"Missing tables: {expected_tables - existing_tables}"

    fact_count = con.execute("SELECT count(*) FROM fact_events").fetchone()[0]
    assert fact_count > 0, "fact_events table is empty"
    con.close()


def test_referential_integrity_no_orphans() -> None:
    """Verify foreign key integrity: every fact row must link to valid dimension keys."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    orphans = con.execute("""
        SELECT count(*) FROM fact_events 
        WHERE repo_key IS NULL 
           OR actor_key IS NULL 
           OR event_type_key IS NULL 
           OR date_key IS NULL
    """).fetchone()[0]
    con.close()
    assert orphans == 0, f"Referential integrity breach: found {orphans} orphan keys"


def test_primary_key_uniqueness() -> None:
    """Verify natural and surrogate key uniqueness across tables."""
    con = duckdb.connect(str(DB_PATH), read_only=True)

    # fact_events event_id
    total_facts = con.execute("SELECT count(*) FROM fact_events").fetchone()[0]
    distinct_facts = con.execute("SELECT count(DISTINCT event_id) FROM fact_events").fetchone()[0]
    assert total_facts == distinct_facts, "Duplicate event_id values found in fact_events"

    # dim_repo repo_key
    total_repos = con.execute("SELECT count(*) FROM dim_repo").fetchone()[0]
    distinct_repos = con.execute("SELECT count(DISTINCT repo_key) FROM dim_repo").fetchone()[0]
    assert total_repos == distinct_repos, "Duplicate repo_key values in dim_repo"

    # dim_actor actor_key
    total_actors = con.execute("SELECT count(*) FROM dim_actor").fetchone()[0]
    distinct_actors = con.execute("SELECT count(DISTINCT actor_key) FROM dim_actor").fetchone()[0]
    assert total_actors == distinct_actors, "Duplicate actor_key values in dim_actor"

    con.close()


def _extract_queries(file_path: Path) -> list:
    """Read SQL file and split on semicolons while stripping comment-only lines."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line for line in f if not line.strip().startswith("--")]
    content = "".join(lines)
    return [q.strip() for q in content.split(";") if q.strip()]


def test_agent_queries_execute_successfully() -> None:
    """Verify that all queries in sql/agent_queries.sql execute cleanly."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    queries = _extract_queries(AGENT_QUERIES_PATH)

    for idx, query in enumerate(queries, start=1):
        try:
            results = con.execute(query).fetchall()
            assert isinstance(results, list), f"Query {idx} did not return a list"
        except Exception as e:
            pytest.fail(f"Agent query {idx} failed with error: {e}")

    con.close()


def test_my_queries_execute_successfully() -> None:
    """Verify that all guided queries in sql/my_queries.sql execute cleanly."""
    con = duckdb.connect(str(DB_PATH), read_only=True)
    queries = _extract_queries(MY_QUERIES_PATH)
    assert len(queries) >= 6, f"Expected at least 6 queries in my_queries.sql, found {len(queries)}"

    for idx, query in enumerate(queries, start=1):
        try:
            results = con.execute(query).fetchall()
            assert isinstance(results, list), f"Query {idx} did not return a list"
        except Exception as e:
            pytest.fail(f"My query {idx} failed with error: {e}")

    con.close()
