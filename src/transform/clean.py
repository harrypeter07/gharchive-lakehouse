"""Clean and transform raw GH Archive events into partitioned Parquet.

Streams raw JSON gzip archives, enforces data quality validation rules,
pseudonymises user identities, and outputs structured, partitioned Parquet datasets
with mathematical reconciliation assertions.
"""

import argparse
import datetime
import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import pyarrow as pa
import pyarrow.dataset as ds

from src.common.config import (
    ACTOR_HASH_SALT,
    ALLOWED_EVENT_TYPES,
    CLEAN_DATA_DIR,
    DEFAULT_DATE,
    PROJECT_ROOT,
    RAW_DATA_DIR,
)
from src.common.dq import DQCounter
from src.transform.reasons import (
    ALL_REASONS,
    DROP_BAD_TIMESTAMP,
    DROP_BOT,
    DROP_CORRUPT_JSON,
    DROP_DUPLICATE_EVENT_ID,
    DROP_EMPTY_TITLE,
    DROP_MISSING_PAYLOAD_ISSUE,
    DROP_UNSUPPORTED_TYPE,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Target PyArrow Schema for Clean Layer
CLEAN_SCHEMA = pa.schema([
    ("event_id", pa.string()),
    ("event_type", pa.string()),
    ("event_date", pa.string()),
    ("created_at", pa.string()),
    ("actor_id", pa.int64()),
    ("actor_login", pa.string()),
    ("actor_hash", pa.string()),
    ("repo_id", pa.int64()),
    ("repo_name", pa.string()),
    ("action", pa.string()),
    ("issue_number", pa.int64()),
    ("issue_title", pa.string()),
    ("issue_body_first_500_chars", pa.string()),
    ("label_names", pa.list_(pa.string())),
    ("pr_merged", pa.bool_()),
])


def hash_actor(login: str, salt: str = ACTOR_HASH_SALT) -> str:
    """Compute salted SHA-256 hash for actor pseudonymisation."""
    token = f"{login.strip().lower()}:{salt}"
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def parse_utc_timestamp(ts_str: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Validate and normalise timestamp into ISO-8601 UTC and date string."""
    if not ts_str or not isinstance(ts_str, str):
        return None, None
    try:
        clean_str = ts_str.replace("Z", "+00:00")
        dt = datetime.datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)
        else:
            dt = dt.astimezone(datetime.timezone.utc)
        iso_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        date_str = dt.strftime("%Y-%m-%d")
        return iso_str, date_str
    except Exception:
        return None, None


def extract_labels(raw_labels: Any) -> List[str]:
    """Extract normalised list of label names from issue or PR payload."""
    if not isinstance(raw_labels, list):
        return []
    result = []
    for item in raw_labels:
        if isinstance(item, dict):
            name = item.get("name")
        else:
            name = str(item)
        if name and isinstance(name, str):
            clean_name = name.strip().lower()
            if clean_name:
                result.append(clean_name)
    return result


def validate_and_extract_row(
    raw_line: str,
    seen_ids: Set[str],
    dq: DQCounter,
) -> Optional[Dict[str, Any]]:
    """Validate a raw line against DQ rules and extract the flattened record."""
    dq.record_read()

    try:
        event = json.loads(raw_line)
        if not isinstance(event, dict):
            dq.record_drop(DROP_CORRUPT_JSON)
            return None
    except Exception:
        dq.record_drop(DROP_CORRUPT_JSON)
        return None

    event_type = event.get("type")
    if event_type not in ALLOWED_EVENT_TYPES:
        dq.record_drop(DROP_UNSUPPORTED_TYPE)
        return None

    event_id = str(event.get("id") or "").strip()
    if not event_id or event_id in seen_ids:
        dq.record_drop(DROP_DUPLICATE_EVENT_ID)
        return None

    actor = event.get("actor") or {}
    actor_login = str(actor.get("login") or "").strip()
    if not actor_login or actor_login.lower().endswith("[bot]"):
        dq.record_drop(DROP_BOT)
        return None

    created_at_raw = event.get("created_at")
    created_at_utc, event_date = parse_utc_timestamp(created_at_raw)
    if not created_at_utc or not event_date:
        dq.record_drop(DROP_BAD_TIMESTAMP)
        return None

    payload = event.get("payload") or {}

    action = payload.get("action")
    issue_number = None
    issue_title = None
    issue_body = None
    label_names = []
    pr_merged = None

    if event_type == "IssuesEvent":
        issue = payload.get("issue")
        if not isinstance(issue, dict):
            dq.record_drop(DROP_MISSING_PAYLOAD_ISSUE)
            return None
        issue_number = issue.get("number")
        raw_title = issue.get("title")
        if raw_title is None or not str(raw_title).strip():
            dq.record_drop(DROP_EMPTY_TITLE)
            return None
        issue_title = str(raw_title).strip()
        issue_body = str(issue.get("body") or "")[:500] if issue.get("body") else None
        label_names = extract_labels(issue.get("labels"))

    elif event_type == "PullRequestEvent":
        pr = payload.get("pull_request") or {}
        issue_number = payload.get("number") or pr.get("number")
        raw_title = pr.get("title")
        if raw_title is None or not str(raw_title).strip():
            dq.record_drop(DROP_EMPTY_TITLE)
            return None
        issue_title = str(raw_title).strip()
        issue_body = str(pr.get("body") or "")[:500] if pr.get("body") else None
        label_names = extract_labels(pr.get("labels"))
        pr_merged = bool(pr.get("merged")) if "merged" in pr else None

    elif event_type == "IssueCommentEvent":
        issue = payload.get("issue") or {}
        issue_number = issue.get("number")
        raw_title = issue.get("title")
        issue_title = str(raw_title).strip() if raw_title else None
        comment = payload.get("comment") or {}
        issue_body = str(comment.get("body") or "")[:500] if comment.get("body") else None

    repo = event.get("repo") or {}
    repo_id = repo.get("id")
    repo_name = repo.get("name") or "unknown/unknown"

    seen_ids.add(event_id)
    dq.record_kept()

    return {
        "event_id": event_id,
        "event_type": event_type,
        "event_date": event_date,
        "created_at": created_at_utc,
        "actor_id": int(actor.get("id")) if actor.get("id") is not None else None,
        "actor_login": actor_login,
        "actor_hash": hash_actor(actor_login),
        "repo_id": int(repo_id) if repo_id is not None else None,
        "repo_name": repo_name,
        "action": str(action) if action is not None else None,
        "issue_number": int(issue_number) if issue_number is not None else None,
        "issue_title": issue_title,
        "issue_body_first_500_chars": issue_body,
        "label_names": label_names,
        "pr_merged": pr_merged,
    }


def write_clean_dataset(
    records: List[Dict[str, Any]],
    output_dir: Path,
    file_prefix: str = "part",
    batch_idx: int = 0,
) -> None:
    """Write cleaned records to partitioned Parquet files."""
    if not records:
        return

    table = pa.Table.from_pylist(records, schema=CLEAN_SCHEMA)
    template = f"{file_prefix}_b{batch_idx}_{{i}}.parquet"

    ds.write_dataset(
        data=table,
        base_dir=output_dir,
        format="parquet",
        partitioning=["event_date", "event_type"],
        partitioning_flavor="hive",
        existing_data_behavior="overwrite_or_ignore",
        basename_template=template,
    )


def generate_dq_report(
    dq: DQCounter,
    output_dir: Path,
    report_md_path: Path,
) -> Dict[str, Any]:
    """Generate machine-readable JSON and human-readable Markdown DQ report."""
    dq_summary = dq.to_dict()
    dq_summary["generated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    json_path = output_dir / "dq_report.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dq_summary, f, indent=2)

    pct_kept = (dq.rows_kept / dq.rows_read * 100) if dq.rows_read else 0
    pct_drop = (dq.total_dropped / dq.rows_read * 100) if dq.rows_read else 0

    md_content = f"""# DATA QUALITY REPORT

**Generated At**: {dq_summary['generated_at']}  
**Reconciliation Status**: {'PASSED (Zero silent drops)' if dq.reconciles() else 'FAILED'}

## 1. Mathematical Reconciliation
$$\\text{{Rows Read}} = \\text{{Rows Kept}} + \\sum \\text{{Dropped}}$$

| Metric | Row Count | Percentage |
| :--- | :--- | :--- |
| **Total Rows Read** | **{dq.rows_read:,}** | 100.00% |
| **Valid Rows Kept** | **{dq.rows_kept:,}** | {pct_kept:.2f}% |
| **Total Rows Dropped** | **{dq.total_dropped:,}** | {pct_drop:.2f}% |

## 2. Drop Breakdown by Reason Code
| Reason Code | Meaning | Dropped Rows | % of Total Read |
| :--- | :--- | :--- | :--- |
"""
    for code, count in dq.dropped_by_reason.most_common():
        meaning = ALL_REASONS.get(code, "Unspecified drop reason")
        pct = (count / dq.rows_read * 100) if dq.rows_read else 0
        md_content += f"| `{code}` | {meaning} | {count:,} | {pct:.2f}% |\n"

    with open(report_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return dq_summary


def clean_file(
    file_path: Path,
    output_dir: Path,
    seen_ids: Set[str],
    dq: DQCounter,
    *,
    batch_size: int = 50_000,
) -> int:
    """Stream one gzip file, clean events in batches, and write to Parquet."""
    import gzip

    clean_records: List[Dict[str, Any]] = []
    file_prefix = file_path.name.replace(".json.gz", "").replace(".jsonl", "").replace(".json", "")
    batch_idx = 0
    total_file_kept = 0

    opener = gzip.open(file_path, "rt", encoding="utf-8", errors="replace") if str(file_path).endswith(".gz") else open(file_path, "rt", encoding="utf-8", errors="replace")

    with opener as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            record = validate_and_extract_row(line, seen_ids, dq)
            if record:
                clean_records.append(record)
                total_file_kept += 1

            if len(clean_records) >= batch_size:
                write_clean_dataset(clean_records, output_dir, file_prefix, batch_idx)
                batch_idx += 1
                clean_records.clear()

    if clean_records:
        write_clean_dataset(clean_records, output_dir, file_prefix, batch_idx)
        clean_records.clear()

    return total_file_kept


def run(
    input_dir: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    report_path: Optional[Path] = None,
    sample_file: Optional[Path] = None,
) -> Dict[str, Any]:
    """Execute complete Clean Layer pipeline across all downloaded raw files."""
    in_dir = input_dir or RAW_DATA_DIR
    out_dir = output_dir or CLEAN_DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    report_md = report_path or (PROJECT_ROOT / "docs" / "DQ_REPORT.md")

    dq = DQCounter()
    seen_ids: Set[str] = set()

    if sample_file:
        files = [sample_file]
    else:
        files = sorted(in_dir.glob("*.json.gz"))

    if not files:
        raise FileNotFoundError(f"No archive files found in {in_dir}")

    logger.info("Cleaning %d files from %s to %s", len(files), in_dir, out_dir)
    for raw_f in files:
        logger.info("Processing %s ...", raw_f.name)
        clean_file(raw_f, out_dir, seen_ids, dq)

    dq.assert_reconciles()
    summary = generate_dq_report(dq, out_dir, report_md)
    logger.info(
        "Clean Layer complete! Read: %d | Kept: %d | Dropped: %d",
        dq.rows_read,
        dq.rows_kept,
        dq.total_dropped,
    )
    return summary


def parse_args() -> argparse.Namespace:
    """Parse CLI options for the cleaner."""
    parser = argparse.ArgumentParser(description="Clean GH Archive events into partitioned Parquet")
    parser.add_argument("--input-dir", type=Path, default=RAW_DATA_DIR, help="Directory containing raw JSON gzip files")
    parser.add_argument("--output-dir", type=Path, default=CLEAN_DATA_DIR, help="Destination directory for Parquet")
    parser.add_argument("--sample-file", type=Path, default=None, help="Process a single sample file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(args.input_dir, args.output_dir, sample_file=args.sample_file)
