# SKILL: porter-stack (what the Porter Data Engineering Intern JD asks for, mapped to this project)
Porter: Indian logistics company (intra-city goods transport marketplace), Google Cloud user. Publicly known: Google Cloud/GKE, Gemini for document extraction, evaluating BigQuery, Metabase + Python/Dash analytics mentioned in job posts. Internal use of Airflow/Spark/Kafka is NOT confirmed. Never claim this project mirrors Porter's stack. Goal: practise the skills the JD names. Verify any Porter claim on their careers page before writing it down.

## JD skill -> where we practise -> what the student must be able to say
- **Python**: all of src/. "Small tested functions; jobs are idempotent."
- **SQL + databases (PostgreSQL/MySQL)**: DuckDB then Postgres. Know JOIN types, GROUP BY, window functions (ROW_NUMBER, SUM OVER), CTEs, indexes, primary/foreign keys, EXPLAIN.
- **ETL**: extract (download), transform (flatten, clean), load (Parquet, DuckDB, Postgres). Know ETL vs ELT.
- **Data warehousing**: star schema (fact = measurements/events with a stated grain; dimension = descriptive context), slowly changing dimensions (concept), OLAP vs OLTP.
- **Airflow**: DAG (tasks with a one-way order, no loops), scheduler, retries, backfill, idempotency, XCom (small values between tasks only).
- **Spark**: distributed DataFrame engine; partitions, lazy evaluation, shuffle, groupBy, windows; when NOT to use it (small data).
- **Kafka**: topic (named log), partition (parallel slice), offset (position), producer/consumer, consumer group; at-least-once delivery means consumers must tolerate duplicates.
- **Cloud (Google Cloud)**: BigQuery (serverless warehouse billed by bytes scanned, so partition and select few columns), Cloud Storage (object store, like our data/ folders), GKE (managed Kubernetes). Free: BigQuery sandbox, no card.
- **Hadoop/Hive concepts**: HDFS = distributed file storage; Hive = SQL over files. Our Parquet + DuckDB/Spark SQL is the modern equivalent. Be able to say this in 2 sentences.
- **Data quality**: reconciliation, null checks, uniqueness, referential integrity, freshness (see skills/data-quality).
- **Clean maintainable code**: tests, small functions, README, pinned versions.
- **Dashboards**: Metabase (open source) in Phase 2.

## Star schema rules for this project
- fact_events grain: one row per GitHub event. Keys: event_id (natural key), repo_key, actor_key, event_type_key, date_key, hour.
- Dimensions get integer surrogate keys. dim_actor stores only a salted hash, never the login.
- Aggregate tables are rebuilt from the fact table by SQL so they can be re-created any time.

## Interview angle
Honest parallels: "event stream per entity (repo) is similar to vehicle/trip events", "hourly peaks resemble demand peaks", "same pipeline skeleton can be reused on delivery data (LaDe)". Do NOT pretend experience with delivery data.

## Keep it current
Before writing a tool version or a Porter fact, verify from official docs or Porter's careers page; cite the URL in DECISIONS.md.
