# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit -> Docker (Postgres, Airflow, Metabase) -> Cloud Deployment (Railway & GitHub).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Docker Desktop (SLIM mode configured)
## Current step
Repository successfully created on GitHub and all commits pushed to https://github.com/harrypeter07/gharchive-lakehouse (origin/main up to date).
## Done and verified
- P1.0 to P1.9: Medallion Lakehouse, zero silent drops (2.05M rows), DuckDB star schema, PySpark cross-engine reconciliation, IR & ML lab, Streamlit app, schema drift test, and master PDF guide.
- P2.1 to P2.4: Docker stack (PostgreSQL, Airflow, Metabase) running locally, DuckDB to PostgreSQL sync (2.05M rows), Airflow DAG active, 23 integration tests.
- GitHub Push (COMPLETE & VERIFIED):
  - Created remote repository `https://github.com/harrypeter07/gharchive-lakehouse`.
  - Pushed all 22 project files and ML/DL weights (`cnn_weights.pt`, `vocab.json`, `splits.parquet`, `demo_lakehouse.duckdb`).
  - Upstream branch tracking verified: `Your branch is up to date with 'origin/main'`.
- Streamlit Execution Page (Tab 3):
  - Live side-by-side execution: Multinomial Naive Bayes + PyTorch 1D-CNN.
  - Live neural tensor diagnostics expander (Token IDs, input tensor `[1, 50]`, Conv1D activations, Max-Pooling `[1, 64]`, output logits).
  - Verified with real in-memory load test: 8,000 index docs, 22,415 vocab, CNN active.
- Academic PDF Report:
  - Authored `docs/DEEP_LEARNING_LAB_REPORT.pdf` (790 KB) in project docs and directly in `C:\Users\ASUS\Downloads\DEEP_LEARNING_LAB_REPORT.pdf`.
## Broken / blocked
(nothing)
## Commands that work
- `git status` (Your branch is up to date with 'origin/main')
- `.\.venv\Scripts\pytest.exe -q` (22 passed, 3 skipped in 27s)
- `.\.venv\Scripts\streamlit.exe run src/app/main.py`
## Next action
Deploy to Railway by selecting `harrypeter07/gharchive-lakehouse` on railway.com, or present `DEEP_LEARNING_LAB_REPORT.pdf` to professor.
## History
- 2026-10-25: P1.0 bootstrapped, P1.1 gate check passed, P1.2 downloaded raw data.
- 2026-10-26: P1.3 cleaned Parquet silver layer, P1.4 built DuckDB star schema, P1.5 reconciled PySpark vs DuckDB, P1.6 evaluated IR and Naive Bayes, P1.7/P1.8/P1.9 completed notebooks, schema drift, Streamlit app, and complete PDF guide.
- 2026-10-26: Phase 2 launched: Docker containers healthy, 2.05M records synchronized to PostgreSQL serving layer, Airflow DAG scheduled, Metabase online.
- 2026-10-27: Authored DL lab README, packaged Railway deployment with Dockerfile, generated DL lab PDF report in Downloads, added DL model tests, enhanced Streamlit live tensor diagnostics, created GitHub repo, and pushed all commits.
