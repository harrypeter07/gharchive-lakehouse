"""Data splitting for Information Retrieval and Machine Learning.

Extracts labeled IssuesEvent records from the DuckDB warehouse,
maps labels to canonical target classes (bug, enhancement, documentation, question),
and partitions the dataset into train (80%), validation (10%), and test (10%) splits
using a deterministic seed.
"""

from pathlib import Path
import random
from typing import Dict, Any, List
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

from src.common.config import CURATED_DATA_DIR, GLOBAL_SEED

# Canonical classification classes in priority order
TARGET_CLASSES = ("bug", "enhancement", "documentation", "question")


def normalize_label(labels: List[str]) -> str | None:
    """Map a list of raw GitHub label strings to a canonical class."""
    if not labels:
        return None
    cleaned = [l.lower().strip() for l in labels if l]
    for lbl in cleaned:
        if "bug" in lbl or "defect" in lbl:
            return "bug"
    for lbl in cleaned:
        if "enhancement" in lbl or "feature" in lbl:
            return "enhancement"
    for lbl in cleaned:
        if "doc" in lbl or "documentation" in lbl:
            return "documentation"
    for lbl in cleaned:
        if "question" in lbl or "help wanted" in lbl:
            return "question"
    return None


def assign_clean_splits(records: list[dict], seed: int = GLOBAL_SEED) -> list[dict]:
    """Keep one issue and token sequence, then split each class reproducibly."""
    from src.ir.index import tokenize
    from src.common.config import DL_MAX_LEN

    seen_issues, seen_texts = set(), set()
    unique = []
    for row in sorted(records, key=lambda r: r["event_id"]):
        issue = (row["repo_name"], row["issue_number"])
        text = tuple(tokenize(f"{row['title']} {row['body']}")[:DL_MAX_LEN])
        if not text or issue in seen_issues or text in seen_texts:
            continue
        seen_issues.add(issue)
        seen_texts.add(text)
        unique.append(dict(row))
    rng = random.Random(seed)
    output = []
    for label in TARGET_CLASSES:
        group = [r for r in unique if r["label"] == label]
        rng.shuffle(group)
        train_end, val_end = int(len(group) * .8), int(len(group) * .9)
        for i, row in enumerate(group):
            row["split"] = "train" if i < train_end else "val" if i < val_end else "test"
        output.extend(group)
    return output


def run_split(
    db_path: Path | None = None,
    output_path: Path | None = None,
    seed: int = GLOBAL_SEED,
    *,
    overwrite: bool = True
) -> Dict[str, Any]:
    """Extract labeled issues, assign splits (80/10/10), and write to Parquet."""
    if db_path is None:
        db_path = Path("data/lakehouse.duckdb")
    if output_path is None:
        output_path = CURATED_DATA_DIR / "splits.parquet"

    if output_path.exists() and not overwrite:
        table = pq.read_table(output_path)
        return {"status": "skipped", "total_rows": len(table)}

    con = duckdb.connect(str(db_path), read_only=True)
    query = """
        SELECT
            f.event_id,
            r.repo_name,
            f.issue_number,
            f.issue_title,
            COALESCE(f.issue_body, '') as issue_body,
            f.label_names
        FROM fact_events f
        JOIN dim_repo r ON f.repo_key = r.repo_key
        WHERE f.has_labels = true
          AND f.issue_title IS NOT NULL
          AND LENGTH(TRIM(f.issue_title)) > 0
    """
    rows = con.execute(query).fetchall()
    con.close()

    labeled_data: List[Dict[str, Any]] = []
    for event_id, repo_name, issue_num, title, body, raw_labels in rows:
        canonical = normalize_label(raw_labels)
        if canonical is not None:
            labeled_data.append({
                "event_id": str(event_id),
                "repo_name": str(repo_name),
                "issue_number": int(issue_num) if issue_num is not None else 0,
                "title": str(title),
                "body": str(body),
                "label": canonical,
            })

    labeled_data = assign_clean_splits(labeled_data, seed)
    n_total = len(labeled_data)
    n_train = sum(d["split"] == "train" for d in labeled_data)
    n_val = sum(d["split"] == "val" for d in labeled_data)
    n_test = sum(d["split"] == "test" for d in labeled_data)

    event_ids = [d["event_id"] for d in labeled_data]
    repo_names = [d["repo_name"] for d in labeled_data]
    issue_numbers = [d["issue_number"] for d in labeled_data]
    titles = [d["title"] for d in labeled_data]
    bodies = [d["body"] for d in labeled_data]
    labels = [d["label"] for d in labeled_data]
    splits = [d["split"] for d in labeled_data]

    table = pa.Table.from_arrays(
        [
            pa.array(event_ids, pa.string()),
            pa.array(repo_names, pa.string()),
            pa.array(issue_numbers, pa.int64()),
            pa.array(titles, pa.string()),
            pa.array(bodies, pa.string()),
            pa.array(labels, pa.string()),
            pa.array(splits, pa.string()),
        ],
        names=["event_id", "repo_name", "issue_number", "title", "body", "label", "split"]
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(table, output_path)

    stats = {
        "total_extracted": n_total,
        "train_count": n_train,
        "val_count": n_val,
        "test_count": n_test,
        "output_path": str(output_path),
    }
    return stats


if __name__ == "__main__":
    result = run_split()
    print(f"Split completed: {result}")
