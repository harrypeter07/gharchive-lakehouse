# START HERE (for YOU, Hassan, not for the agent)

## What is in this pack
```
00_START_HERE.md            <- you are here
01_MASTER_PROMPT.md         <- paste this FIRST into Antigravity
02_PHASE_PROMPTS.md         <- paste these ONE AT A TIME, in order
repo_files/                 <- copy this whole folder's contents into your project root
  AGENTS.md                 <- the agent's rulebook
  docs/CONTEXT.md           <- agent's memory of project state (agent updates it)
  docs/BUGS.md              <- bug log (agent updates it)
  docs/DECISIONS.md         <- why we chose X (agent updates it)
  docs/PORTER_NOTES.md      <- YOUR hand-written learning notes
  skills/*/SKILL.md         <- 9 skill files
```

## Honest expectation
Phase 1 + Phase 2 in "one go" realistically means 2 to 3 long days, not one. The agent types fast; the slow parts are downloads, Docker image pulls, debugging and YOU understanding things. If you only have one day, finish Phase 1 steps 1 to 6 and stop. A finished small project beats an unfinished big one.

## Part 1: One-time setup (do these yourself, ~45 min)

Define: **terminal** = the text window where you type commands. **Repo** = project folder tracked by git. **API key** = a secret password string that lets your code call a service.

1. **Git**: install from https://git-scm.com. Check: `git --version`.
2. **Python 3.11**: install from https://www.python.org/downloads/ (tick "Add to PATH" on Windows). Check: `python --version`.
3. **GitHub account** (you have one: @harrypeter07). Create an EMPTY repo called `gharchive-lakehouse`. Keep it public (portfolio) but never commit keys.
4. **Gemini key**: go to https://aistudio.google.com/apikey, sign in, click "Create API key". Copy it. Free tier has request limits per minute/day that change over time, so the agent will check current limits at https://ai.google.dev/gemini-api/docs/rate-limits.
5. **Docker Desktop** (needed only for Phase 2):
   - Windows: install from https://www.docker.com/products/docker-desktop/ . It needs WSL 2 (Windows Subsystem for Linux, a built-in Linux layer). The installer offers to enable it. Restart when asked. Docker Desktop is free for personal use and education.
   - Mac: same site, pick Apple Silicon or Intel chip version.
   - Linux: install Docker Engine + compose plugin from https://docs.docker.com/engine/install/ .
   - Check: `docker --version` and `docker run hello-world`.
   - RAM: full stack wants ~8 GB free. If your laptop has 8 GB total, use the "slim" stack (Postgres + Airflow + Metabase only). The agent will ask your RAM and choose.
   - Define: **Docker** = runs programs in sealed boxes (containers) so they work the same on every machine. **Docker Compose** = one file that starts many containers together.
6. **Antigravity**: open your project folder in it. Create `.env` (a file for secrets) later via the agent; it will put `GEMINI_API_KEY=...` there and add `.env` to `.gitignore` so it never uploads.
7. **Google Colab** (for lab submission): https://colab.research.google.com , free tier is enough for one day of data.
8. Optional Phase 2 extras, all free: Metabase (open-source dashboard tool, runs in Docker). No cloud account needed. BigQuery sandbox is optional: https://cloud.google.com/bigquery/docs/sandbox (no credit card, limited free quota). Skip it unless you have time.

## Part 2: How to run the build
1. Copy everything inside `repo_files/` into your project root.
2. Open Antigravity in that folder. Paste `01_MASTER_PROMPT.md`. Wait until the agent confirms it read all rules and asks you the setup questions.
3. Paste prompts from `02_PHASE_PROMPTS.md` one at a time. Do NOT paste the next until the current one's "DONE CHECK" passes and you have reviewed it.
4. If the agent loops on a bug for more than 3 attempts, tell it: "Stop. Read skills/bug-solving/SKILL.md and follow Section: Stuck protocol."

## Part 3: What the agent does vs what YOU must do
Agent does: boilerplate, downloading, flattening code, Parquet writing, Docker files, DAG scaffolding, Streamlit UI, tests, README formatting.

YOU do yourself (this is your Porter interview material; do not delegate):
1. Write 6 to 8 SQL queries on the star schema by hand in `sql/my_queries.sql`, then explain each out loud.
2. Write the data quality rules (what counts as a bad row) in your own words in `docs/PORTER_NOTES.md` BEFORE the agent writes them. Then compare.
3. Draw (on paper, not in the repo) the pipeline: raw -> clean -> curated. Be able to say why each layer exists.
4. Write the Airflow DAG's task order yourself on paper; let the agent code it; then read every line.
5. After every phase, close the agent and answer the "EXPLAIN-BACK" questions in PORTER_NOTES.md from memory. Cannot answer = go back and ask the agent to teach you that piece.
6. Run `docker compose up` and `docker compose down` yourself and read the logs once.
7. Be able to answer: "Why Parquet, not CSV?", "Why a star schema?", "What happens if the DAG runs twice?" (idempotency), "Why did rows drop?"

## Part 4: Rules for staying honest on your resume
- Say: "Built a data lakehouse pipeline on public GH Archive data."
- Do NOT say it uses Porter data or Porter's stack. Do NOT claim Kafka production experience; say "replayed hourly files through Kafka in a local Docker setup."
- Only list tools you can explain for 5 minutes.
