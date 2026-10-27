# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit -> Docker (Postgres, Airflow, Metabase) -> Cloud Deployment (Railway & GitHub).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Docker Desktop (SLIM mode configured)
## Current step
Completed data deduplication (14,780 clean issues, zero split leakage), retrained PyTorch 1D-CNN with class-weighting, completed modular dark navy UI tabs, authored DL_LAB_GUIDE.md, and regenerated DEEP_LEARNING_LAB_REPORT.pdf (889 KB).
## Done and verified
- P1.0 to P1.9: Medallion Lakehouse, zero silent drops (2.05M rows), DuckDB star schema, PySpark cross-engine reconciliation, IR & ML lab, Streamlit app, schema drift test, and master PDF guide.
- P2.1 to P2.4: Docker stack (PostgreSQL, Airflow, Metabase) running locally, DuckDB to PostgreSQL sync (2.05M rows), Airflow DAG active, 27 integration tests.
- Data Audit & Model Retraining:
  - Deduplicated repeated issues (551 duplicates removed); 14,780 clean records split into train (11,823), val (1,478), test (1,479) with zero token sequence overlap.
  - Re-trained 1D-CNN: 1,297,412 parameters, 20,075 vocab size, test accuracy 77.15%, Macro-F1 62.34%.
  - Real metrics saved to `data/curated/dl_report.json` with zero fabricated numbers.
- Streamlit Modular UI:
  - Compact navy theme (`.streamlit/config.toml`), cyan charts, and modular tab files (`src/app/tabs/`).
  - Native "Lab guide" tab backed by comprehensive `docs/DL_LAB_GUIDE.md`.
  - Live tensor diagnostics (`[1, 50]` -> `[1, 64, 50]` -> `[1, 64]` -> 4 probabilities) with word ID inspection.
- Academic PDF Report:
  - Freshly updated [C:\Users\ASUS\Downloads\DEEP_LEARNING_LAB_REPORT.pdf](file:///C:/Users/ASUS/Downloads/DEEP_LEARNING_LAB_REPORT.pdf) (889 KB) with Child-Friendly "Explain Like I'm 10" section and honest per-class evaluation.
- Test Suite: 27 passed, 3 skipped in 36s.
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
