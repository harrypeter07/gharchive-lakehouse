# SKILL: bug-solving
Use for: ANY error, failing test, wrong number, slow job, or weird output.

## Protocol (do in order; do not skip)
1. **Copy the exact error text**. Do not paraphrase.
2. **Reproduce** with the smallest input (one hour file, 100 rows). Write the command that reproduces it.
3. **Read the error bottom-up**: last line = what, lines above = where. Find the first line that is OUR code.
4. **Write 2 to 3 hypotheses** before changing anything. Rank them.
5. **Test one hypothesis at a time** with a print/assert/small experiment. Change ONE thing per attempt.
6. **Search official docs/issue trackers** using the exact error message. Prefer official docs, then GitHub issues, then StackOverflow. Cite the URL in BUGS.md.
7. **Fix, then add a test or assert** so it cannot silently return.
8. **Log in docs/BUGS.md** (template inside). Update CONTEXT.md.

## Common failure map for THIS project
- MemoryError / Colab crash: you loaded too much. Stream, subsample, select columns from Parquet, query files with DuckDB.
- JSON KeyError: a field is missing in some events. Use `.get()` and count how often it is missing; do not assume.
- Row counts do not reconcile: some branch drops rows without a reason code. Add the reason.
- DuckDB/Spark mismatch: check timezone, duplicates, NULL handling, integer vs float, and whether both read the same partitions.
- Spark Kafka connector errors: Spark version + Scala version + connector version must match EXACTLY. Print all three.
- Spark "Java not found/unsupported": check Java version against the Spark docs.
- Docker: container exits -> `docker compose logs <service>`; port in use -> change host port; out of memory -> SLIM mode; volume permission errors -> check ownership.
- Airflow DAG missing: check import errors (`airflow dags list-import-errors`).
- Gemini 429/quota: rate limit hit -> sleep, batch, cache; never retry in a tight loop.
- CNN not learning: check labels align with text, class imbalance, learning rate, vocab size, and that loss drops to ~0 when training on 50 samples (overfit test).

## Stuck protocol (after 3 failed attempts)
STOP. Write in chat: what you tried, results, your best remaining hypothesis, and 2 options (smaller scope, or workaround). Ask the student to choose. Never keep looping silently, and never delete tests to get green.
