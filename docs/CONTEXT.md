# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit. Phase 2: Docker (Postgres, Airflow, Kafka/Spark streaming, Metabase).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Not installed / in PATH (reserved for Phase 2)
## Current step
P1.4 Curated layer (DuckDB star schema)
## Done and verified
- P1.0 Bootstrap complete: folder hierarchy, `.gitignore`, `.env.example`, `.env`, initial git commit.
- P1.1 Gate Check passed: confirmed Plan A (GitHub natural labels as ground truth).
- P1.2 Full day raw layer complete: 18 verified hours (2.01 GB, ~4.5M events), manifest test passed.
- P1.3 Clean layer (Silver) complete:
  - Authored `src/transform/clean.py` with multi-batch partitioned Parquet output.
  - Processed 18 raw files: 3,826,476 rows read -> 2,057,052 rows kept -> 1,769,424 rows dropped.
  - Zero silent drops mathematically asserted (`rows_read == rows_kept + sum(dropped)`).
  - Drops cataloged: `UNSUPPORTED_TYPE`: 906,577; `BOT_ACTOR`: 862,845; `DUPLICATE_EVENT_ID`: 2.
  - Generated `docs/DQ_REPORT.md` and `data/clean/dq_report.json`.
  - Pseudonymised actors using salted SHA-256 (`actor_hash`).
  - All 7 tests passing (`pytest -q`).
## Broken / blocked
(nothing)
## Label coverage (measured in P1.1 & P1.3)
- Target: 2024-06-10 events
- Cleaned IssuesEvent count: 53,134 rows across 21,650 unique repositories
- Plan: Plan A (GitHub natural labels as ground truth)
## Commands that work
- `py -3.11 -m venv .venv`
- `.\.venv\Scripts\pytest.exe -q`
- `.\.venv\Scripts\python.exe -m src.transform.clean`
- `.\.venv\Scripts\python.exe -m src.transform.inspect_clean`
## Next action
Build `src/warehouse/build_star.sql` and `src/warehouse/build.py` to create `data/lakehouse.duckdb`.
## History
- 2026-10-25: P1.0 bootstrapped repo and gitignore.
- 2026-10-25: P1.1 executed single-hour analysis, confirmed label coverage metrics.
- 2026-10-25: P1.2 downloaded raw layer (2.01 GB, 18 verified files, manifest test passed).
- 2026-10-26: P1.3 transformed raw layer into partitioned Parquet silver layer (2,057,052 clean rows).
