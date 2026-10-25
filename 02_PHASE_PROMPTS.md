# PHASE PROMPTS (paste ONE at a time; wait for DONE CHECK to pass)

Each prompt starts with "Before you start" so a forgetful agent re-reads its memory. Keep that line.

Final target folder layout the agent must create (do not change names):
```
gharchive-lakehouse/
  AGENTS.md  README.md  requirements.txt  .env.example  .gitignore
  docs/ CONTEXT.md BUGS.md DECISIONS.md GLOSSARY.md PORTER_NOTES.md DQ_REPORT.md RESULTS.md
  skills/ ...
  data/raw/ data/clean/ data/curated/ data/lakehouse.duckdb   (git-ignored)
  src/ingest/ src/transform/ src/warehouse/ src/spark/ src/ir/ src/ml/ src/app/ src/common/
  sql/ my_queries.sql  agent_queries.sql
  tests/
  notebooks/ ir_lab.ipynb  dl_lab.ipynb
  docker/ docker-compose.yml  airflow/dags/  spark/  metabase/
```

---

## PHASE 1 (Colab-compatible, lab deliverable)

### P1.0 Bootstrap
Before you start: read AGENTS.md, docs/CONTEXT.md, docs/BUGS.md, and the skills you need (say which).
Do:
1. Based on my OS answers, give me exact commands to create a virtual environment (a private Python install per project) and activate it.
2. Create the folder layout above, `.gitignore` (must ignore `.env`, `data/`, `*.duckdb`, `__pycache__`, `.venv`), `.env.example` with `GEMINI_API_KEY=` placeholder, and empty `requirements.txt`.
3. Ask me to create `.env` myself by copying `.env.example` and pasting my key. Do NOT ask me to paste the key into chat.
4. Initialise git, connect to my GitHub repo `gharchive-lakehouse` (ask me for the URL), first commit.
5. Use skills/free-tier-guard: fetch the CURRENT Gemini free-tier limits from https://ai.google.dev/gemini-api/docs/rate-limits and the current free model names from https://ai.google.dev/gemini-api/docs/models and write them in docs/DECISIONS.md with the date. Do not rely on memory for these.
DONE CHECK: `git log` shows 1 commit, `.env` not tracked (`git status` clean), CONTEXT.md filled.

### P1.1 Inspect ONE hour and measure label coverage (GATE; most important check)
Before you start: re-read docs/CONTEXT.md and skills/data-quality.
Do:
1. Download exactly one file: `https://data.gharchive.org/2024-06-10-15.json.gz` (hour has NO leading zero) into `data/raw/`. If the date 404s, try another recent full date and note it.
2. Without loading everything into memory, read it line by line (each line is one JSON event). Print: file size, number of events, count per event `type`, and for `IssuesEvent` rows count how many have a non-empty `payload.issue.labels` list. Print the top 20 label names.
3. Print 3 raw example IssuesEvent JSON lines so I can see the real structure. Explain in simple words what `actor`, `repo`, `payload`, `created_at` mean.
4. Write results to docs/CONTEXT.md under "Label coverage".
5. Decision rule (write into DECISIONS.md):
   - If labeled IssuesEvent rows with a bug/feature/question-like label are >= ~1.5% of IssuesEvent rows AND a full day would give >= 3,000 labeled rows, use GitHub labels as ground truth (Plan A).
   - Otherwise use Plan B: take a sample of issue titles, label them with Gemini free tier (skills/free-tier-guard: batch, cache every answer to `data/cache/gemini_labels.jsonl`, respect rate limits, sleep between calls), and VALIDATE Gemini against the real GitHub labels on the labeled subset and report agreement %. Call these "silver labels" in all reports; never call them ground truth.
   - Note: an "opened" issue is often created with no labels; labels may be added in later "labeled" events. Report how many `action` values exist (opened, closed, labeled...).
DONE CHECK: I can see the numbers, and the plan (A or B) is written down with the numbers as reason. STOP and show me the numbers; I confirm the plan.

### P1.2 Download one full day (raw layer)
Before you start: re-read CONTEXT.md and free-tier-guard.
Do:
1. Write `src/ingest/download_gharchive.py` with arguments `--date YYYY-MM-DD`. It downloads 24 hourly files with retries, a polite pause between requests, resumes (skips files already downloaded and verified by size > 0), and writes a `data/raw/manifest.json` listing filename, bytes, download time.
2. Check free disk space first and tell me the total download size before proceeding.
3. Write a test that the manifest has 24 entries (or lists which hours are missing).
4. Cite the data source and terms: link https://www.gharchive.org/ in README.
DONE CHECK: 24 files (or explained gaps), manifest exists, test passes.

### P1.3 Clean layer (silver) + data quality report
ME FIRST: I will write the data quality rules in docs/PORTER_NOTES.md section "My DQ rules" (what is a bad row? what is a duplicate? what about bots?). Agent: create the template with those headings, then WAIT for me to say "rules written". Then:
Before you start: read skills/data-quality and skills/testing.
Do:
1. Write `src/transform/clean.py` that streams each hourly file, keeps event types: IssuesEvent, PullRequestEvent, PushEvent, WatchEvent, ForkEvent, IssueCommentEvent, and flattens to columns: event_id, event_type, created_at (UTC timestamp), actor_login, actor_id, repo_id, repo_name, action, issue_number, issue_title, issue_body_first_500_chars, label_names (list), pr_merged (bool), etc. Inspect real data to confirm field names; do not invent.
2. Rules (combine MY rules with these): drop bots (login ends with `[bot]`), drop empty/whitespace titles for issue/PR rows only, drop duplicate event_id, normalise timestamps to UTC, record every drop with a reason code.
3. Write Parquet partitioned by `event_date` and `event_type` to `data/clean/`. Explain partitioning in plain words.
4. Produce `docs/DQ_REPORT.md` and a machine-readable `data/clean/dq_report.json`: rows read, rows per drop reason, rows written. ASSERT `rows_read == rows_written + sum(dropped)`; the program must FAIL if not.
5. Re-run must give identical output (idempotent: running twice does not duplicate). Test it.
6. Pseudonymise actors: store `actor_hash` = SHA-256 of (login + a secret salt from `.env`) in curated layer; do not expose raw logins in the app.
DONE CHECK: assertion passes, DQ_REPORT shows numbers, double-run test passes. I review the report and compare with my own rules.
YOU (me): explain-back questions in PORTER_NOTES.md answered from memory.

### P1.4 Curated layer: DuckDB star schema
ME FIRST: sketch on paper which tables you think are facts vs dimensions; then tell the agent. Agent builds its own and we compare.
Before you start: read skills/porter-stack (section Star schema) and skills/testing.
Do:
1. Create `data/lakehouse.duckdb` with `fact_events`, `dim_repo`, `dim_actor` (hash only), `dim_event_type`, `dim_date`, plus `agg_stars_per_repo_day` and `agg_events_per_hour`. Build via SQL in `src/warehouse/build_star.sql`, run by `src/warehouse/build.py`. Explain fact vs dimension, primary key, foreign key, surrogate key in plain words with examples from our tables.
2. Add checks: no orphan foreign keys (every fact row finds its dimension row), row count of fact equals clean row count, no duplicate keys.
3. Write 5 example queries in `sql/agent_queries.sql` with a comment explaining each.
4. ME: I write 6 to 8 queries myself in `sql/my_queries.sql` (top repos by stars, hourly activity, issue-open vs close ratio, window function ranking, etc). Agent only RUNS them and helps fix syntax, never writes them for me.
DONE CHECK: all integrity checks pass; my queries run.

### P1.5 PySpark reconcile
Before you start: read skills/porter-stack (section Spark) and skills/free-tier-guard.
Do:
1. Check Java is installed (Spark needs Java 17 or 11, check current Spark docs for supported versions); if not, give me a guide. Pin PySpark version in requirements.txt after checking docs. Record in DECISIONS.md.
2. `src/spark/agg_job.py`: read `data/clean/` Parquet, compute stars per repo per day and events per hour, write result.
3. `tests/test_spark_vs_duckdb.py`: the same two aggregates from Spark and DuckDB must match exactly; fail otherwise.
4. Explain in plain words: what is Spark, why not just pandas, what is a partition, what is lazy evaluation, what is a shuffle.
DONE CHECK: test passes. If Spark is too slow or breaks on my machine after 3 attempts, follow bug-solving Stuck protocol and tell me; we can run this step in Colab instead.

### P1.6 IR lab: BM25, language model, Naive Bayes
Before you start: read skills/coding, skills/testing, skills/learning-coach.
Do:
1. Split data FIRST: train/validation/test by time or random with fixed seed 42, saved to `data/curated/splits.parquet`. All text statistics (vocabulary, IDF, priors) are computed on train only. Explain "data leakage" simply.
2. `src/ir/index.py`: tokeniser (lowercase, split on non-letters, keep a short stopword list), inverted index (word -> list of documents containing it), written from scratch (no search library). Then `bm25.py` with parameters k1=1.5, b=0.75 and `lm.py` unigram language model with Dirichlet smoothing. Explain each formula in words, then give the formula.
3. Tests: a known rare word ranks its only matching doc first; an empty query returns nothing without crashing.
4. Evaluation: build a 20-query set (agent drafts 20, I review and fix). Relevance judgement: a document is relevant if it contains all the query's key terms AND is from the labeled set; say honestly this is a weak proxy. Report precision@5, precision@10, MAP for BM25 vs LM in `docs/RESULTS.md`.
5. Naive Bayes from scratch (multinomial, add-one smoothing) on classes from the P1.1 plan; compare to a majority-class baseline; confusion matrix as a TEXT table.
DONE CHECK: tests pass, RESULTS.md has real numbers.

### P1.7 DL lab: neural classifier
Before you start: read skills/coding and skills/testing. Choose PyTorch (free). Pin version.
Do:
1. 1D-CNN text classifier (embedding -> convolution -> pooling -> linear). Train on the same split. Seed fixed. Log train/validation loss and accuracy per epoch to `docs/RESULTS.md` as a text table. Early stopping on validation.
2. Compare 4 models: majority baseline, Naive Bayes, CNN, and optional logistic regression on TF-IDF (a strong simple baseline). Report macro-F1 as well as accuracy (explain why accuracy misleads when classes are uneven).
3. If CNN does not beat Naive Bayes, REPORT THAT HONESTLY and write 3 likely reasons. Do not tune on the test set.
4. Optional (only if time): hourly activity forecast with an LSTM vs "same hour last week" baseline.
5. Make it train on CPU in under ~10 minutes on one day of data (subsample if needed); give Colab GPU instructions as optional.
DONE CHECK: comparison table exists, test set was touched only once at the end.

### P1.8 Streamlit app
Before you start: read skills/design.
Do:
1. `src/app/main.py` with 4 tabs: Trends (top growing repos, events by hour), Search (query box, BM25 or LM selector, top 10 results with scores, highlight matched words), Classifier (paste text, show predictions from Naive Bayes and CNN with probabilities), Data Quality (reads dq_report.json, shows the reconciliation). Optional 5th tab: "Ask in English", Gemini converts a question into a SQL query, shows the SQL, runs it READ-ONLY on DuckDB (only SELECT allowed; reject everything else).
2. Cache heavy loads with Streamlit's caching.
3. Give me commands to run locally, and a Colab recipe using a free tunnel (try `cloudflared` quick tunnel first because it needs no account; fall back to localtunnel; ngrok needs a free account and token, so only then guide me step by step).
DONE CHECK: app opens, all 4 tabs work with real data, no keys visible in the UI or git.

### P1.9 Lab notebooks + README
Do:
1. `notebooks/ir_lab.ipynb` and `notebooks/dl_lab.ipynb` that clone my GitHub repo in Colab, install pinned requirements, run on ONE day, and run top to bottom. Each has a markdown intro, results, and conclusion in plain English.
2. README: problem, data source + link + citation, text architecture description (no images), how to run, results table, limitations (silver labels, one day only, weak relevance judgements), what I would do next.
DONE CHECK: restart Colab runtime and Run All succeeds.

---

## PHASE 2 (Docker, local)

Gate: Phase 1 DONE CHECKs all passed AND I have answered all explain-back questions. If not, refuse to start Phase 2 and tell me what is missing.

### P2.0 Docker sanity
Do: guide me to verify `docker --version`, `docker compose version`, `docker run hello-world`. Ask RAM; if under 12 GB total, choose SLIM mode (Postgres + Airflow + Metabase; Kafka/Spark streaming later and only if memory allows). Record in DECISIONS.md. Explain image, container, volume, port mapping, network in plain words.

### P2.1 Postgres warehouse
Do: `docker/docker-compose.yml` with Postgres (pinned image tag), a named volume, credentials from `.env`, a healthcheck. `src/warehouse/load_postgres.py` loads curated tables (same star schema, Postgres SQL types). Make load idempotent (running twice = same row counts; explain upsert vs truncate+load). Test row counts vs DuckDB.
ME: write 3 Postgres queries and note one syntax difference from DuckDB in PORTER_NOTES.md.

### P2.2 Airflow
ME FIRST: write the DAG task order on paper: download -> clean -> dq check -> build star -> load postgres -> spark agg. Tell the agent.
Do: Airflow in Docker (use the official docker-compose approach from current Airflow docs; check the docs for the current version, pin it, use LocalExecutor to save RAM). DAG `gharchive_daily` with parameter `date`, retries, a data-quality task that FAILS the DAG if reconciliation fails, tasks idempotent. Explain DAG, task, operator, scheduler, backfill, idempotency, catchup. Run for 2 different days.
Explain-back in PORTER_NOTES: what happens if hour 17 file is missing? what if the DAG re-runs?

### P2.3 Kafka + Spark Structured Streaming (skip in SLIM mode)
Do: single-node Kafka (KRaft mode, no Zookeeper; check current image docs, use free `apache/kafka` image), topic `gh_events`. `src/ingest/replay_producer.py` reads one day's hourly files and publishes events with a speed factor. Spark Structured Streaming job reads the topic, counts events per repo per 5-minute window, writes to Postgres. Pin the Spark-Kafka connector to match the Spark and Scala version EXACTLY (write both in DECISIONS.md). Explain topic, partition, producer, consumer, offset, consumer group, watermark, window.
If it fails 3 times, mark as "attempted" in CONTEXT.md and move on. Do not burn the day here.

### P2.4 Metabase
Do: add Metabase (open-source image) to compose, connect to Postgres, give me click-by-click steps. ME: build 3 dashboard cards by clicking: top repos, events per hour, issue open vs closed. Export screenshots NOT needed; describe in README text.

### P2.5 Optional: BigQuery sandbox
Only if I say yes. Guide me to the sandbox (no credit card), run ONE query on the public `githubarchive` dataset scanning a small partition, and compare the count to our DuckDB number for the same hour. Show the bytes-processed estimate BEFORE running each query (free tier is limited).

### P2.6 Finish
Do: final README update, `docs/RESULTS.md` complete, a `docs/INTERVIEW_QA.md` with 25 questions an interviewer might ask about THIS project with short answers based on what was actually built (flag any answer where the project does not actually support the claim). Then ask me the questions one by one, quiz style, and tell me which answers were weak.
