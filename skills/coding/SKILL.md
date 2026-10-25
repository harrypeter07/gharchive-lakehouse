# SKILL: coding
Use for: writing or changing any Python/SQL/shell code.

## Rules
1. Python 3.11, type hints on function signatures, docstring of 1-3 lines saying WHAT and WHY.
2. One job per function (under ~40 lines). One job per file. Folder = layer (ingest, transform, warehouse, spark, ir, ml, app).
3. No magic numbers: put paths, seeds, thresholds in `src/common/config.py`. Read secrets only from env vars via `os.environ` (load `.env` with python-dotenv).
4. Stream big files line by line (`gzip.open(..., "rt")`); never load a whole day of JSON into memory.
5. Use `pathlib.Path`, not string paths. Use `logging`, not stray `print` (print is fine for demo output).
6. Seeds: set `random`, `numpy`, `torch` seeds to 42 in one helper `set_seed()`.
7. Make jobs idempotent: running twice gives the same result. Write to a temp path then rename, or overwrite the partition.
8. Fail loudly: raise an error with a clear message instead of returning silently wrong results.
9. Before adding a library, ask: is it free, maintained, needed? Record in DECISIONS.md. Pin version.
10. Never copy-paste code you cannot explain. Add a "How it works" comment for any non-obvious block.

## Pattern for a pipeline step
`def run(input_path, output_path, *, overwrite=False) -> dict` returns stats (rows in, rows out) so tests and the DQ report can use them.

## Checklist before saying done
- Runs from a clean terminal. - Has a test. - No secrets. - CONTEXT.md updated. - Explained to the student.
