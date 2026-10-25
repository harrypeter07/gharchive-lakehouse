# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit. Phase 2: Docker (Postgres, Airflow, Kafka/Spark streaming, Metabase).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (via `py -3.11`)  Docker: Not installed / in PATH (reserved for Phase 2)
## Current step
P1.0 Bootstrap
## Done and verified
- Inspected system environment: confirmed Windows, 16 GB RAM, Git 2.45.2, Python 3.11 installed.
- Created full project directory structure: data layers, src packages, sql, tests, notebooks, docker.
- Configured `.gitignore` (ignoring `.env`, `data/`, `*.duckdb`, `__pycache__`, `.venv`).
- Created `.env.example` with placeholders for `GEMINI_API_KEY` and `ACTOR_SALT`.
- Created empty `requirements.txt` and base `README.md`.
- Recorded D-001 in `docs/DECISIONS.md` verifying Gemini free-tier limits (15 RPM / 1M TPM / 1500 RPD) from official documentation.
## Broken / blocked
(nothing)
## Label coverage (filled in P1.1)
(not measured yet)
## Commands that work
- `py -3.11 --version` -> Python 3.11
- `git --version` -> git version 2.45.2.windows.1
## Next action
Student creates `.env` from `.env.example`; initialize git repo and make first commit.
## History
- 2026-10-25: Step 0 completed. System inspected, rules reviewed, directory tree scaffolded.
