# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit -> Docker (Postgres, Airflow, Metabase) -> Cloud Deployment (Railway).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Docker Desktop (SLIM mode configured)
## Current step
Streamlit Execution Tab Enhanced with Live Neural Tensor Traces & Interactive Buttons; All Commits Staged and Ready for GitHub Push.
## Done and verified
- P1.0 to P1.9: Medallion Lakehouse, zero silent drops (2.05M rows), DuckDB star schema, PySpark cross-engine reconciliation, IR & ML lab, Streamlit app, schema drift test, and master PDF guide.
- P2.1 to P2.4: Docker stack (PostgreSQL, Airflow, Metabase) running locally, DuckDB to PostgreSQL sync (2.05M rows), Airflow DAG active, 23 integration tests.
- Deep Learning Verification & Lab README:
  - Verified genuine PyTorch model: `IssueCNN` with 1,447,172 trainable parameters, Adam optimizer ($lr=10^{-3}$), CrossEntropyLoss.
  - Weights serialized at `data/curated/cnn_weights.pt` (5.79 MB) and `vocab.json` (22,553 tokens).
  - Authored beginner-friendly `docs/DEEP_LEARNING_README.md` with post office analogy, viva Q&A, and terminal proof.
- Cloud Deployment on Railway:
  - Authored production `Dockerfile` (Python 3.11-slim, CPU PyTorch, dynamic `$PORT` binding).
  - Created `railway.json`, `.dockerignore`, and step-by-step `docs/RAILWAY_DEPLOYMENT_GUIDE.md`.
  - Created standalone 8.1 MB `data/curated/demo_lakehouse.duckdb` to allow full cloud analytics without hitting GitHub's 100 MB file limit.
- Academic PDF Report:
  - Authored `scripts/generate_dl_report_pdf.py` generating `docs/DEEP_LEARNING_LAB_REPORT.pdf` (790 KB).
  - Copied directly to `C:\Users\ASUS\Downloads\DEEP_LEARNING_LAB_REPORT.pdf`.
- Streamlit Execution Page (Tab 3):
  - Enhanced Tab 3 with live side-by-side execution: Multinomial Naive Bayes + PyTorch 1D-CNN.
  - Added live tensor diagnostics expander (Token IDs, input tensor `[1, 50]`, Conv1D activations, Max-Pooling `[1, 64]`, output logits).
  - Verified with real in-memory load test: 8,000 index docs, 22,415 vocab, CNN active.
- Git Commits:
  - Clean local git commits: `05da019` and `5282e5c`.
## Broken / blocked
- Direct headless `git push` requires interactive GitHub authentication (GCM). Student needs to run `git push -u origin main` in their terminal.
## Commands that work
- `.\.venv\Scripts\pytest.exe -q` (22 passed, 3 skipped in 27s)
- `.\.venv\Scripts\python.exe -m py_compile src/app/main.py`
- `.\.venv\Scripts\streamlit.exe run src/app/main.py`
- `git push -u origin main` (in student's interactive terminal)
## Next action
Student runs `git push -u origin main` in PowerShell/terminal, then tests Streamlit locally or deploys to Railway.
## History
- 2026-10-25: P1.0 bootstrapped, P1.1 gate check passed, P1.2 downloaded raw data.
- 2026-10-26: P1.3 cleaned Parquet silver layer, P1.4 built DuckDB star schema, P1.5 reconciled PySpark vs DuckDB, P1.6 evaluated IR and Naive Bayes, P1.7/P1.8/P1.9 completed notebooks, schema drift, Streamlit app, and complete PDF guide.
- 2026-10-26: Phase 2 launched: Docker containers healthy, 2.05M records synchronized to PostgreSQL serving layer, Airflow DAG scheduled, Metabase online.
- 2026-10-27: Authored DL lab README, packaged Railway deployment with Dockerfile, generated DL lab PDF report in Downloads, added DL model tests, and enhanced Streamlit live tensor diagnostics.
