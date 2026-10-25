# DECISIONS (agent: add entry per choice)
Template: ## D-001 | date | topic
- Chosen:  - Why:  - Alternatives rejected:  - Revisit if:

## D-001 | 2026-10-25 | Gemini Free-Tier Limits and Model Selection
- **Chosen**: `gemini-1.5-flash` / `gemini-2.0-flash` for any optional LLM silver-labeling or SQL helper tasks.
- **Current Official Limits (verified from https://ai.google.dev/gemini-api/docs/rate-limits and https://ai.google.dev/gemini-api/docs/models)**:
  - RPM (Requests Per Minute): 15 RPM
  - TPM (Tokens Per Minute): 1,000,000 TPM
  - RPD (Requests Per Day): 1,500 RPD
  - Quota reset: Daily at midnight Pacific Time (PT)
- **Why**: Fastest response times, highest daily quota (1,500 RPD vs 50 RPD for Pro), and completely free without credit card.
- **Alternatives rejected**: `gemini-1.5-pro` (capped at 2 RPM / 50 RPD in free tier, too small for batch work); paid APIs.
- **Revisit if**: Google modifies free-tier quotas or model deprecation notices are posted on ai.google.dev.

## D-002 | 2026-10-25 | Issue Classification Ground Truth: Plan A (GitHub Natural Labels)
- **Chosen**: Plan A (use GitHub's natural labels as ground truth for IR and ML classification).
- **Measurement Details**:
  - Command: `.\.venv\Scripts\python.exe -m src.ingest.inspect_one_hour`
  - Target: `data/raw/2024-06-10-15.json.gz` (Date: 2024-06-10, Hour: 15 UTC)
  - Total events scanned: 263,102
  - Denominator: All `IssuesEvent` rows = 4,381 rows
  - Numerator: `IssuesEvent` rows with non-empty `payload.issue.labels` = 1,953 rows (44.58%)
  - Action breakdown of denominator (4,381): opened: 2,486 (56.7%), closed: 1,815 (41.4%), reopened: 80 (1.8%)
  - Target category subset (bug, enhancement/feature, question, doc): ~907 rows (~20.7% of all IssuesEvent rows)
- **Why**: 1,953 labeled issues in a single hour projects to ~21,600+ labeled rows across the verified dataset, exceeding the 3,000 threshold required for supervised learning.
- **Alternatives rejected**: Plan B (Gemini silver labels) reserved strictly as an auxiliary/validation option.
- **Revisit if**: Full-day cleaned dataset shows unexpected class sparsity.

## D-003 | 2026-10-25 | Development Date & Schema Drift Test Strategy
- **Chosen**: Use `2024-06-10` as the fixed development day for building and verifying the pipeline, without redownloading. At the conclusion of Phase 1, run the complete pipeline on a recent date (`2026-10-24`) to explicitly test schema drift and reproducibility.
- **Why**: `2024-06-10` was provided as an initial example date in the lab prompt. Testing against a recent 2026 date at the end of Phase 1 provides real-world validation of schema stability (e.g. field renames, label distribution shifts, event volume differences).
- **Alternatives rejected**: Re-downloading a new date mid-development (would waste bandwidth and invalidate 2.01 GB of verified cache).
- **Revisit if**: Upstream GH Archive schema changes break extraction on the 2026 date.

## D-004 | 2026-10-25 | Phase 2 SLIM Docker Stack & Pinned Image Versions
- **Chosen**: SLIM mode Docker stack comprising PostgreSQL, Apache Airflow (LocalExecutor), and Metabase:
  - PostgreSQL: `postgres:16.3-alpine` (official lightweight Alpine image, https://hub.docker.com/_/postgres)
  - Apache Airflow: `apache/airflow:2.9.2-python3.11` with LocalExecutor (official Docker Compose guide: https://airflow.apache.org/docs/apache-airflow/2.9.2/howto/docker-compose/index.html)
  - Metabase: `metabase/metabase:v0.49.13` (official OSS BI image: https://www.metabase.com/docs/v0.49/installation-and-operation/running-metabase-on-docker)
- **Why**: LocalExecutor runs scheduler and worker in a single process without needing Celery or Redis, conserving ~2 GB RAM. Alpine Postgres minimizes image size and startup latency.
- **Alternatives rejected**: CeleryExecutor Airflow with Redis (wastes ~1.5 GB RAM locally); heavy Ubuntu-based Postgres images.
- **Revisit if**: Kafka/Spark streaming is added after Phase 1 and local RAM permits.
