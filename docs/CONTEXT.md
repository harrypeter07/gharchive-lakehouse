# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit -> Docker (Postgres, Airflow, Metabase) -> Cloud Deployment (Railway & GitHub).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Docker Desktop (SLIM mode configured)
## Current step
College Practicals Alignment (Practicals 3, 4, 5, 6, 7) fully implemented in Streamlit Tab 3, README, and regenerated PDF report; pushed commit 7989e7f to https://github.com/harrypeter07/gharchive-lakehouse.
## Done and verified
- P1.0 to P1.9: Medallion Lakehouse, zero silent drops (2.05M rows), DuckDB star schema, PySpark cross-engine reconciliation, IR & ML lab, Streamlit app, schema drift test, and master PDF guide.
- P2.1 to P2.4: Docker stack (PostgreSQL, Airflow, Metabase) running locally, DuckDB to PostgreSQL sync (2.05M rows), Airflow DAG active, 23 integration tests.
- GitHub Push & Railway Auto-Deploy:
  - Repository: `https://github.com/harrypeter07/gharchive-lakehouse`.
  - Pushed commit `7989e7f` (`feat(dl): align deep learning tab with college practicals 3-6 and update lab report`).
  - Branch up to date with `origin/main`.
- Streamlit Execution Page (Tab 3):
  - Fixed button click triggers using `st.session_state` and `st.rerun()`.
  - Integrated 4 dedicated college practical studios:
    - Practical 6: Exact 2D matrix convolution ($X \in 4\times 4, K \in 3\times 3 \implies FM \in 2\times 2$, Stride 1, Padding 0, Flattening, Dense layer, Sigmoid).
    - Practical 4: Study of 6 Optimizers (Vanilla GD, Momentum, NAG, Adagrad, RMSProp, Adam) + Batching strategies with interactive loss curves.
    - Practical 5: Study of Regularizers (L1, L2, Dropout, Early Stopping) with overfitting prevention curves.
    - Practical 3: Feedforward Neural Network architecture with ReLU and Softmax.
  - Live side-by-side execution: Multinomial Naive Bayes + PyTorch 1D-CNN.
  - Verified with real in-memory load test: 8,000 index docs, 22,415 vocab, CNN active.
- Academic PDF Report:
  - Authored and compiled `docs/DEEP_LEARNING_LAB_REPORT.pdf` (877 KB) including the RCOEM CSE college practicals section, and copied to `C:\Users\ASUS\Downloads\DEEP_LEARNING_LAB_REPORT.pdf`.
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
