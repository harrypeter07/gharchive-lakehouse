# SKILL: data-quality
Use for: any cleaning, filtering, dedup, joins, or loading step.

1. **Reconcile**: rows_in = rows_out + rows_dropped (sum of every reason). Assert in code.
2. **Every drop has a reason code** (BOT, EMPTY_TITLE, DUPLICATE_EVENT_ID, BAD_TIMESTAMP, UNSUPPORTED_TYPE...). Never drop silently.
3. **Checks per layer**: row counts; null rate per column; unique key; value ranges (timestamps inside the requested day); allowed values (event types); referential integrity (every fact foreign key exists in its dimension); freshness (latest event time).
4. **Raw is immutable**: never edit raw files.
5. **Idempotent**: re-running gives identical outputs; compare row counts/hash.
6. **Report**: write `docs/DQ_REPORT.md` and `dq_report.json` every run (date, rows per reason, null rates).
7. **Fail the pipeline** when a check fails (nonzero exit / failed Airflow task) rather than writing bad data.
8. **Privacy**: pseudonymise actors (salted SHA-256), aggregate by repo/hour, never rank or track individual people.

## Label quality (ML)
State where labels come from (GitHub labels vs Gemini silver labels). Measure agreement on the overlap. Report class balance. Never mix silver and gold labels in the test set without saying so.
