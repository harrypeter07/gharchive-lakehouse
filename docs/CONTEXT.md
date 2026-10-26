# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit -> Docker (Postgres, Airflow, Metabase).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Docker Desktop 29.9.2 running (SLIM mode active)
## Current step
Phase 2 Complete: Docker stack launched, DuckDB synchronized to PostgreSQL warehouse, Airflow DAG active, Metabase BI healthy, 23/23 tests passing.
## Done and verified
- P1.0 to P1.9: Complete Medallion Lakehouse, zero silent drops (2.05M rows), DuckDB star schema, PySpark cross-engine reconciliation, IR & ML lab, Streamlit app, schema drift test, and complete PDF guide.
- P2.1 Docker Stack Launch:
  - `lakehouse_postgres` (`postgres:16.3-alpine`) on port 5432: UP & HEALTHY.
  - `lakehouse_airflow_init`: Database migrations complete, admin user created.
  - `lakehouse_airflow_webserver` (`apache/airflow:2.9.2-python3.11`) on port 8080: UP & HEALTHY.
  - `lakehouse_airflow_scheduler`: UP & ACTIVE (LocalExecutor).
  - `lakehouse_metabase` (`metabase/metabase:v0.49.13`) on port 3000: UP & HEALTHY.
- P2.2 Warehouse Export:
  - Authored `src/warehouse/export_postgres.py` using DuckDB's postgres extension.
  - Exported: `dim_date` (1), `dim_event_type` (6), `dim_repo` (514k), `dim_actor` (483k), `agg_stars_per_repo_day` (69,326), `agg_events_per_hour` (108), `fact_events` (2,057,052).
- P2.3 Airflow DAG:
  - Authored `docker/airflow/dags/gharchive_dag.py` (`gharchive_daily_lakehouse`).
- P2.4 Testing:
  - Added `tests/test_phase2_docker.py` verifying container health, Metabase API, and Airflow webserver.
  - All 23 tests passing (`pytest -q`).
## Broken / blocked
(nothing)
## Commands that work
- `.\.venv\Scripts\pytest.exe -q` (23 passed in 20s)
- `.\.venv\Scripts\python.exe -m src.warehouse.export_postgres`
- `$env:PATH = "C:\Users\ASUS\AppData\Local\Programs\DockerDesktop\resources\bin;" + $env:PATH; docker compose -f docker/docker-compose.yml ps`
## Next action
Review Airflow Web UI at http://localhost:8080 and Metabase BI at http://localhost:3000.
## History
- 2026-10-25: P1.0 bootstrapped, P1.1 gate check passed, P1.2 downloaded raw data.
- 2026-10-26: P1.3 cleaned Parquet silver layer, P1.4 built DuckDB star schema, P1.5 reconciled PySpark vs DuckDB, P1.6 evaluated IR and Naive Bayes, P1.7/P1.8/P1.9 completed notebooks, schema drift, Streamlit app, and complete PDF guide.
- 2026-10-26: Phase 2 launched: Docker containers healthy, 2.05M records synchronized to PostgreSQL serving layer, Airflow DAG scheduled, Metabase online.
