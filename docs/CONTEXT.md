# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit. Phase 2: Docker (Postgres, Airflow, Kafka/Spark streaming, Metabase).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Not installed / in PATH (reserved for Phase 2)
## Current step
P1.3 Clean layer (Silver) scaffolding & DQ rules alignment
## Done and verified
- P1.0 Bootstrap complete: folder hierarchy, `.gitignore`, `.env.example`, `.env`, initial git commit.
- P1.1 Gate Check passed: confirmed Plan A with exact denominator/numerator metrics.
- P1.2 Full day raw layer complete:
  - Resilient downloader `src/ingest/download_gharchive.py` with DNS fallback, socket timeouts, and atomic gzip verification.
  - Downloaded 18 full verified hourly files (2.01 GB total compressed data, ~4.5M events).
  - Documented explained gaps for 6 hours (6, 8, 9, 13, 19, 21) due to transient public CDN dropouts.
  - Generated `data/raw/manifest.json` with 24 hourly entries.
  - Configured `pytest.ini` and passed `tests/test_download_manifest.py` (100% green).
- Scaffolding for P1.3 pre-work: test fixtures, drop reason codes, and DQ reconciliation helper.
## Broken / blocked
- Final `src/transform/clean.py` is BLOCKED on student writing DQ rules in `docs/PORTER_NOTES.md`.
## Label coverage (measured in P1.1)
- Target file: `data/raw/2024-06-10-15.json.gz` (Date: 2024-06-10, Hour: 15 UTC)
- Total Events: 263,102
- Denominator: All `IssuesEvent` rows = 4,381 rows (1.67% of all events)
- Numerator: `IssuesEvent` rows with non-empty `payload.issue.labels` = 1,953 rows (44.58%)
- Denominator Action Breakdown: opened (2,486), closed (1,815), reopened (80)
- Target category subset (bug, enhancement/feature, question, documentation): ~907 rows (~20.7% of issues)
- Plan: Plan A (GitHub natural labels as ground truth). At end of Phase 1, run schema-drift test on 2026-10-24.
## Commands that work
- `py -3.11 -m venv .venv`
- `.\.venv\Scripts\python.exe -m src.ingest.inspect_one_hour`
- `.\.venv\Scripts\pytest.exe -q`
## Next action
Student finishes writing DQ rules in `docs/PORTER_NOTES.md`. Then build final `clean.py` using rules.
## History
- 2026-10-25: P1.0 bootstrapped repo and gitignore.
- 2026-10-25: P1.1 executed single-hour analysis, confirmed label coverage metrics.
- 2026-10-25: P1.2 downloaded raw layer (2.01 GB, 18 verified files, manifest test passed).
