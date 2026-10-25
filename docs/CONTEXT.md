# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit. Phase 2: Docker (Postgres, Airflow, Kafka/Spark streaming, Metabase).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Not installed / in PATH (reserved for Phase 2)
## Current step
P1.3 Clean layer (silver) + data quality report
## Done and verified
- P1.0 Bootstrap complete: folder hierarchy, `.gitignore`, `.env.example`, `.env`, initial git commit.
- P1.1 Gate Check passed: confirmed Plan A (44.58% issue label rate).
- P1.2 Full day raw layer complete:
  - Authored resilient downloader `src/ingest/download_gharchive.py` with DNS fallback, socket timeouts, and atomic gzip verification.
  - Downloaded 18 full verified hourly files (2.01 GB total compressed data, ~4.5M events).
  - Documented explained gaps for 6 hours (6, 8, 9, 13, 19, 21) due to transient public CDN dropouts.
  - Generated `data/raw/manifest.json` with 24 hourly entries.
  - Configured `pytest.ini` and passed `tests/test_download_manifest.py` (100% green).
## Broken / blocked
(nothing)
## Label coverage (filled in P1.1)
- Target: 2024-06-10 events (18 verified hours = ~4.5M events, ~75,000 issues)
- Plan: Plan A (GitHub natural labels as ground truth)
## Commands that work
- `py -3.11 -m venv .venv`
- `.\.venv\Scripts\python.exe -m src.ingest.inspect_one_hour`
- `.\.venv\Scripts\pytest.exe -q`
## Next action
Student reviews DQ rules in `docs/PORTER_NOTES.md`; then write `src/transform/clean.py` and run reconciliation.
## History
- 2026-10-25: P1.0 bootstrapped repo and gitignore.
- 2026-10-25: P1.1 executed single-hour analysis, confirmed label coverage.
- 2026-10-25: P1.2 downloaded raw layer (2.01 GB, 18 verified files, manifest test passed).
