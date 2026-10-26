# CONTEXT (agent keeps this current)
## Project
gharchive-lakehouse: GH Archive -> clean Parquet -> DuckDB star schema -> Spark check -> IR + ML -> Streamlit. Phase 2: Docker (Postgres, Airflow, Metabase).
## Student environment
OS: Windows  RAM: 16 GB  Python: 3.11 (in .venv)  Docker: Docker Desktop 29.9.2 running (containers reserved for Phase 2)
## Current step
Phase 1 Complete (P1.0 to P1.9 verified). Ready for Phase 2 Docker stack launch.
## Done and verified
- P1.0 Bootstrap complete: folder hierarchy, `.gitignore`, `.env.example`, `.env`, initial git commit.
- P1.1 Gate Check passed: confirmed Plan A (GitHub natural labels as ground truth).
- P1.2 Full day raw layer complete: 18 verified hours (2.01 GB, ~3.8M events), manifest test passed.
- P1.3 Clean layer (Silver) complete:
  - 3,826,476 rows read -> 2,057,052 rows kept -> 1,769,424 rows dropped.
  - Zero silent drops mathematically asserted (`rows_read == rows_kept + sum(dropped)`).
  - Hive-style partitioned Parquet written to `data/clean/event_date=2024-06-10/event_type=*/`.
  - Pseudonymised actors via salted SHA-256 (`actor_hash`).
- P1.4 Curated layer (Gold DuckDB) complete:
  - Built `data/lakehouse.duckdb`: `fact_events` (2.05M rows), `dim_repo` (514k), `dim_actor` (483k), `dim_event_type` (6), `dim_date` (1). 0 orphan keys.
  - Authored & verified 6 analytical queries in `sql/my_queries.sql` and 5 in `sql/agent_queries.sql`.
- P1.5 PySpark Cross-Engine Reconciliation complete:
  - Installed `pyspark==3.5.1` and `py4j==0.10.9.7`.
  - Audited aggregations against DuckDB: exact match across 69,328 starred repos and 108 hourly bins in UTC.
- P1.6 Information Retrieval (IR) Lab complete:
  - 80/10/10 disjoint split (13,622 train / 1,702 val / 1,704 test).
  - Built InvertedIndex (53k vocab), BM25, and Unigram Language Model with Dirichlet smoothing (&mu;=2000).
  - Trained Multinomial Naive Bayes (75.94% accuracy, 56.22% macro-F1).
- P1.7 Deep Learning Lab complete:
  - Authored 1D-CNN architecture (`src/ml/dataset.py`, `src/ml/model.py`, `src/ml/train.py`).
- P1.8 Streamlit App complete:
  - Interactive 4-tab UI created in `src/app/main.py`.
- P1.9 Lab Notebooks & Benchmarks complete:
  - Interactive notebooks created in `notebooks/ir_lab.ipynb` and `notebooks/dl_lab.ipynb`.
  - Schema drift tested on `2026-10-24-15` (36,829 events, 80.35% labeled rate, 100% backward-compatible).
  - Publication-grade guide and vector PDF generated: `docs/GHARCHIVE_LAKEHOUSE_COMPLETE_GUIDE.pdf` (1.26 MB).
  - All 20 tests passing (`pytest -q`).
## Broken / blocked
(nothing)
## Commands that work
- `.\.venv\Scripts\pytest.exe -q` (20 passed in 17s)
- `.\.venv\Scripts\python.exe -m src.transform.clean`
- `.\.venv\Scripts\python.exe -m src.warehouse.build`
- `.\.venv\Scripts\python.exe -m src.spark.agg_job`
- `.\.venv\Scripts\python.exe -m src.ir.evaluate`
- `.\.venv\Scripts\python.exe -m scripts.generate_guide_pdf`
## Next action
Begin Phase 2: Start Docker SLIM stack (`docker compose -f docker/docker-compose.yml up -d`) and build automated Airflow DAGs.
## History
- 2026-10-25: P1.0 bootstrapped, P1.1 gate check passed, P1.2 downloaded raw data.
- 2026-10-26: P1.3 cleaned Parquet silver layer, P1.4 built DuckDB star schema.
- 2026-10-26: P1.5 reconciled PySpark vs DuckDB, P1.6 evaluated IR and Naive Bayes, P1.7/P1.8/P1.9 completed notebooks, schema drift, Streamlit app, and comprehensive guide PDF.
