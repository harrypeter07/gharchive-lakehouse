# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit. Phase 2: Docker (Postgres, Airflow, Kafka/Spark streaming, Metabase).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Not installed / in PATH (reserved for Phase 2)
## Current step
P1.1 Inspect ONE hour and measure label coverage (Gate Check)
## Done and verified
- P1.0 Bootstrap complete: folder hierarchy, `.gitignore`, `.env.example`, `.env`, initial git commit.
- Downloaded `2024-06-10-15.json.gz` (141.65 MB, 263,102 events).
- Streamed line-by-line inspection via `src/ingest/inspect_one_hour.py`.
- Measured label coverage: 4,381 IssuesEvent rows; 1,953 rows (44.58%) carry labels.
- Verified bug/feature/question categories exceed 20% of IssuesEvent rows, yielding ~21,600 projected labeled rows per day.
## Broken / blocked
(nothing)
## Label coverage (filled in P1.1)
- File inspected: `2024-06-10-15.json.gz` (141.65 MB)
- Total Events: 263,102
- IssuesEvent count: 4,381 (1.67% of all events)
- IssuesEvent with labels: 1,953 (44.58% of issues)
- Target category breakdown (bug, enhancement/feature, question, documentation): ~900 rows/hr (~20.5% of issues)
- Full-day projection: ~21,600 target labeled rows (> 3,000 required for Plan A)
- Action breakdown: opened (2,486), closed (1,815), reopened (80)
## Commands that work
- `py -3.11 -m venv .venv`
- `.\.venv\Scripts\python.exe -m src.ingest.inspect_one_hour`
## Next action
Hassan confirms Plan A selection; proceed to P1.2 Download one full day.
## History
- 2026-10-25: P1.0 bootstrapped repo and gitignore.
- 2026-10-25: P1.1 executed single-hour analysis, confirmed label coverage.
