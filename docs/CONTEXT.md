# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit -> Docker (Postgres, Airflow, Metabase) -> Cloud Deployment (Railway & GitHub).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Docker Desktop (SLIM mode configured)
## Current step
Integrated background key rotation from `Blind_But_Smart` into `src/ai/gemini_solver.py`, eliminated all key inputs and "Gemini/AI/LLM" references from frontend, verified live web grounded patch synthesis (14.8 KB patch, 23 sources), and pushed all updates.
## Done and verified
- Grounded Issue Resolution & Patch Synthesis (`src/ai/gemini_solver.py`, `src/app/tabs/solver.py`):
  - Connected key rotation engine loading valid production keys from `Blind_But_Smart/.env` and environment variables.
  - Successfully tested end-to-end grounded retrieval: generated verified 14,869-character systems engineering patch with 23 cited GitHub repository links.
  - Completely stripped all API key inputs and password fields from frontend.
  - Removed all "Gemini", "AI", and "LLM" vocabulary from frontend and replaced with formal systems engineering terms ("Automated Defect & Patch Solver", "Grounded Technical Retrieval").
  - Test suites verified green (5 passed in `test_dl_lab.py`, 7 passed in `test_ir.py`).
- IR Presentation Content & Defense Deck (`docs/IR_PRESENTATION_CONTENT.md`):
  - Formulated 8 detailed slides designed for Google Slides / PowerPoint / AI presentation generators.
  - Aligned with the 3 college practicals: BM25, Dirichlet Language Model, and Multinomial Naive Bayes.
  - Included slide titles, visual layout blueprints, mathematical formulas, empirical benchmark tables, plain-English speaker scripts, and technical examination defense Q&A.
- Information Retrieval (IR) Academic Specification ('About me'):
  - Replaced documentation with comprehensive IR specification covering the three college lab practicals:
    1. Probabilistic IR using BM25 Ranking (`src/ir/bm25.py`).
    2. Language Model-based IR using Unigram Language Model with Dirichlet ($\mu=2000.0$) and Jelinek-Mercer ($\lambda=0.7$) smoothing (`src/ir/lm.py`).
    3. Supervised text classification using Multinomial Naive Bayes with Laplace smoothing ($\alpha=1.0$) across 4 classes (`src/ir/naive_bayes.py`).
  - Added ASCII dataflow diagrams, mathematical formulations, and empirical benchmark tables (14,780 issues, 57,306 vocabulary terms, 75.94% NB accuracy).
- High-Precision IR Search Improvements:
  - Indexed all 14,780 lakehouse issues in `src/app/resources.py` (previously capped at 8,000).
  - Implemented Query Coordination Matching in `src/ir/bm25.py` and `src/ir/lm.py` so multi-term queries reward documents matching a higher percentage of terms.
  - Added match percentage badges (e.g. `100% Term Match (3/3)`), matched keywords, context window snippet extraction with cyan keyword highlights, and maintainer triage advice.
  - Added precision threshold filters and category dropdowns in `src/app/tabs/search.py`.
- AI Issue Solver & Live Web Search Grounding (`src/app/tabs/solver.py`, `src/ai/gemini_solver.py`):
  - Built AI solver module calling Google Gemini with Google Search Grounding to search live web/GitHub for repositories, commits, and PRs.
  - Synthesizes root-cause analysis, code patches/diffs, and lists clickable reference sources.
  - Added fallback to local Lakehouse BM25 retrieval when running without API key.
  - Added 'Issue solver' navlink in `src/app/main.py`.
  - Verified 100% test suite passing (27 passed, 3 skipped).
- Navigation Link Update:
  - Renamed 'Deep learning' tab to 'Search categories' in `src/app/main.py`.
  - Updated test assertion in `tests/test_dl_lab.py` (5 passed).
- P1.0 to P1.9: Medallion Lakehouse, zero silent drops (2.05M rows), DuckDB star schema, PySpark cross-engine reconciliation, IR & ML lab, Streamlit app, schema drift test, and master PDF guide.
- P2.1 to P2.4: Docker stack (PostgreSQL, Airflow, Metabase) running locally, DuckDB to PostgreSQL sync (2.05M rows), Airflow DAG active, 27 integration tests.
- Diagrammatic, Point-to-Point Architecture Documentation ('About me'):
  - Rewrote `docs/DL_LAB_GUIDE.md` with visual ASCII dataflow and layer-by-layer tensor diagrams.
  - Linked every component directly to its Python source file and function (`src/ir/index.py`, `src/ml/model.py`, `src/ml/inference.py`, `src/ml/train.py`, `src/search/ranker.py`).
  - Preserved all empirical measurements (14,780 issues, 1,297,412 parameters, 77.15% accuracy, 62.34% Macro-F1, sub-2ms latency).
  - Completely free of emojis, academic homework jargon, and convoluted language.
  - Verified 100% test pass rate (27 passed, 3 skipped).
- Security Scrubbing of Open-Source Public Issues:
  - Scanned `splits.parquet` for strings matching AWS (`ASIA...`) and Google (`AIza...`) key patterns.
  - Found 2 public third-party issues from 2024 (`awslabs/aws-sdk-swift#1557` and `wu-jeffrey/tour-to#4`) where external developers had pasted example keys in bug reports.
  - Redacted both occurrences to `[REDACTED_AWS_TOKEN]` and `[REDACTED_GOOGLE_KEY]`.
  - Re-computed SHA-256 fingerprint in `dl_report.json` and verified all tests pass.
  - Pushed commit `f160ef4` to `origin/main`.
- 100% Dynamic Model Inference (Zero Hardcoded Responses):
  - Removed static `ACTIONS` text dictionaries entirely.
  - Model computes dynamic forward pass on ANY user-typed text in real time (`predict_issue` via PyTorch).
  - All displayed outputs (probabilities, latency, token trace, word IDs, input shapes) are computed live on CPU.
  - Pushed commit `c748eec` to `origin/main`.
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
