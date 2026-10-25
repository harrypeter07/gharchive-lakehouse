# SKILL: testing
Use for: any function that transforms data, and before saying "done".
- Use `pytest`. Tests in `tests/`, named `test_<module>.py`. Run `pytest -q` and show output.
- Tiny fixtures: 5 to 20 hand-written JSON lines in `tests/fixtures/`, including bad cases (bot, empty title, duplicate id, missing field, weird timestamp).
- Must-have tests: row reconciliation; idempotent re-run; Spark == DuckDB aggregates; BM25 rare word ranks its only document first; empty query is safe; train/val/test have no overlap; fact table has no orphan keys.
- Test failure paths too (corrupt gzip, missing hour).
- A test must be able to FAIL: briefly break the code to confirm it fails.
- Never delete or loosen a test to get green without telling the student why.
