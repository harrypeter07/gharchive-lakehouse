# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit -> Docker (Postgres, Airflow, Metabase) -> Cloud Deployment (Railway & GitHub).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Docker Desktop (SLIM mode configured)
## Current step
Rebranded 'Lab guide' to 'About me' with professional, emoji-free system architecture and engineering documentation authored by Hassan; pushed commit 037af25 to GitHub.
## Done and verified
- P1.0 to P1.9: Medallion Lakehouse, zero silent drops (2.05M rows), DuckDB star schema, PySpark cross-engine reconciliation, IR & ML lab, Streamlit app, schema drift test, and master PDF guide.
- P2.1 to P2.4: Docker stack (PostgreSQL, Airflow, Metabase) running locally, DuckDB to PostgreSQL sync (2.05M rows), Airflow DAG active, 27 integration tests.
- Professional System Documentation ('About me'):
  - Transformed the guide into a rigorous, publication-grade technical specification authored by Hassan (RCOEM CSE).
  - Completely removed emojis and classroom/homework framing ("aligning with lab practicals").
  - Detailed the full Deep Learning architecture (Tokenization, 64-dim embeddings, 1D-Conv, Global Max-Pooling, Dropout 0.2, Multi-Class Softmax).
  - Outlined empirical benchmarks (77.15% accuracy, 62.34% Macro-F1), data deduplication audit (14,780 issues), and cloud infrastructure.
  - Pushed commit `037af25` to `origin/main`.
- Practical & Actionable Prediction Output:
  - Deep Learning 1D-CNN performs 4-class categorization (Bug, Enhancement, Docs, Question).
  - Added maintainer actionable recommendations for each class (e.g. defect verification, backlog review).
  - Embedded real lakehouse similarity search (`BM25Ranker`) to retrieve real past matching issues from the 8,000 indexed records so developers can see real past discussions and fixes.
  - Zero hardcoded or faked data.
  - Pushed commit `432a636` to `origin/main`.
- UI Visibility & Response Polish:
  - Added large verdict banner with category emoji badge (`🐞 Bug`, `✨ Enhancement`, `📚 Documentation`, `❓ Question`) and exact neural confidence %.
  - Added 4-card percentage breakdown for all classes, plus comparison table of 1D-CNN vs. Naive Bayes.
  - Added plain-language explanation of why words like 'configure' get classified as Enhancement (real class imbalance).
  - Added 'What Are We Doing Here?' overview expander at the top of the Deep Learning page.
  - Pushed commit `3671374` to `origin/main`.
- Presentation Slides & Lab Defense Deck:
  - Authored 8-slide presentation deck with child-like pitch scripts, technical defense details, and empirical benchmark tables.
  - Exported [C:\Users\ASUS\Downloads\DL_PRESENTATION_SLIDES_AND_GUIDE.pdf](file:///C:/Users/ASUS/Downloads/DL_PRESENTATION_SLIDES_AND_GUIDE.pdf) (1,029,049 bytes) in Downloads folder.
  - Pushed commit `6f6ca78` to `origin/main` on GitHub.
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
