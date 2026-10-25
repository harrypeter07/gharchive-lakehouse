# gharchive-lakehouse

A demonstration data lakehouse pipeline built on public GitHub Archive event data.
Ingests hourly compressed events, transforms and reconciles them into partitioned Parquet, builds a star schema in DuckDB, verifies metrics with PySpark, trains information retrieval and neural classification models on issue text, and visualises trends in Streamlit.
Phase 2 extends this architecture to Docker with PostgreSQL, Apache Airflow orchestration, and Metabase.

## Data Source & Citation
- **Source**: [GH Archive](https://www.gharchive.org/)
- **Data URL**: `https://data.gharchive.org/YYYY-MM-DD-H.json.gz`
- Public archive of GitHub events made available under the GitHub Terms of Service.

## Architecture
1. **Raw Layer (`data/raw/`)**: Hourly compressed JSON gzip files directly from GH Archive with manifest verification.
2. **Clean Layer (`data/clean/`)**: Reason-coded filtering (dropping bots, empty titles, duplicates), UTC normalization, pseudonymisation, partitioned Parquet.
3. **Curated Layer (`data/lakehouse.duckdb`)**: Star schema with `fact_events` and dimensions (`dim_repo`, `dim_actor`, `dim_event_type`, `dim_date`) plus aggregates.
4. **Processing & Verification**: DuckDB SQL analytics verified against PySpark DataFrame aggregations.
5. **Machine Learning & IR**: Inverted index BM25 search, language modeling, Naive Bayes classifier, and 1D-CNN neural classifier.
6. **Presentation**: Streamlit multi-tab analytical application (Trends, Search, Classifier, DQ Reconciliation).
7. **Production Sandbox**: Dockerized Postgres, Airflow DAGs, Kafka replay, and Metabase dashboards.

## How to Run
*(Setup and execution commands will be updated as modules are built)*

## Results
*(Populated during P1.6, P1.7, and Phase 2)*

## Limitations
- Operates on a sample slice of GH Archive events.
- Issue labels may rely on silver labels if natural label coverage is sparse.
- Local execution environment limits scale compared to distributed clusters.

## Next Steps
- Production cloud deployment on GCP (BigQuery / GCS).
- Streaming ingestion via Kafka KRaft.
