"""Inspect one hourly GH Archive file and measure label coverage.

Downloads a single compressed hour file from GH Archive, streams events line by line,
and measures event distribution and issue label prevalence.
"""

import gzip
import json
import logging
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

from src.common.config import RAW_DATA_DIR, SAMPLE_DATE_HOUR, SAMPLE_URL

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def download_file(url: str, dest_path: Path) -> Path:
    """Download a remote file if it does not already exist with content."""
    if dest_path.exists() and dest_path.stat().st_size > 0:
        logger.info("File already exists: %s (%d bytes)", dest_path.name, dest_path.stat().st_size)
        return dest_path

    logger.info("Downloading %s to %s ...", url, dest_path)
    req = urllib.request.Request(url, headers={"User-Agent": "gharchive-lakehouse/1.0"})
    with urllib.request.urlopen(req) as response, open(dest_path, "wb") as out_file:
        while chunk := response.read(1024 * 1024):
            out_file.write(chunk)

    logger.info("Downloaded %s successfully (%d bytes)", dest_path.name, dest_path.stat().st_size)
    return dest_path


def analyze_hourly_file(file_path: Path) -> Dict[str, Any]:
    """Stream one hourly gzip file and calculate event and label statistics."""
    total_events = 0
    event_type_counts: Counter[str] = Counter()
    issue_actions: Counter[str] = Counter()
    issues_total = 0
    issues_with_labels = 0
    label_counts: Counter[str] = Counter()
    sample_issues: List[Dict[str, Any]] = []

    with gzip.open(file_path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            total_events += 1
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            event_type = event.get("type", "Unknown")
            event_type_counts[event_type] += 1

            if event_type == "IssuesEvent":
                issues_total += 1
                payload = event.get("payload", {})
                action = payload.get("action", "unknown")
                issue_actions[action] += 1

                issue = payload.get("issue", {})
                labels = issue.get("labels", [])
                if labels:
                    issues_with_labels += 1
                    for label in labels:
                        if isinstance(label, dict):
                            label_name = label.get("name", "").strip().lower()
                        else:
                            label_name = str(label).strip().lower()
                        if label_name:
                            label_counts[label_name] += 1

                if len(sample_issues) < 3:
                    sample_issues.append(event)

    return {
        "file_bytes": file_path.stat().st_size,
        "total_events": total_events,
        "event_types": event_type_counts,
        "issues_total": issues_total,
        "issues_with_labels": issues_with_labels,
        "issue_actions": issue_actions,
        "top_labels": label_counts.most_common(20),
        "sample_issues": sample_issues,
    }


def run() -> Dict[str, Any]:
    """Execute download and inspection of the sample hour."""
    target_path = RAW_DATA_DIR / f"{SAMPLE_DATE_HOUR}.json.gz"
    download_file(SAMPLE_URL, target_path)
    results = analyze_hourly_file(target_path)

    print("\n" + "=" * 60)
    print("GH ARCHIVE HOURLY INSPECTION & LABEL COVERAGE REPORT")
    print("=" * 60)
    print(f"Target: {SAMPLE_DATE_HOUR}.json.gz")
    print(f"File Size: {results['file_bytes'] / (1024 * 1024):.2f} MB")
    print(f"Total Events: {results['total_events']:,}")

    print("\n--- Event Distribution ---")
    for ev_type, count in results["event_types"].most_common():
        pct = (count / results["total_events"]) * 100 if results["total_events"] else 0
        print(f"  {ev_type:<25}: {count:>7,} ({pct:5.2f}%)")

    print("\n--- IssuesEvent Analysis ---")
    print(f"Total IssuesEvent rows: {results['issues_total']:,}")
    pct_labeled = (
        (results["issues_with_labels"] / results["issues_total"]) * 100
        if results["issues_total"]
        else 0
    )
    print(
        f"IssuesEvent with labels: {results['issues_with_labels']:,} ({pct_labeled:5.2f}%)"
    )

    print("\n--- IssuesEvent Action Distribution ---")
    for action, count in results["issue_actions"].most_common():
        print(f"  {action:<15}: {count:>6,}")

    print("\n--- Top 20 Issue Label Names ---")
    for label, count in results["top_labels"]:
        print(f"  {label:<30}: {count:>5,}")

    print("\n" + "=" * 60)
    print("3 RAW ISSUESEVENT SAMPLES (Summarized fields)")
    print("=" * 60)
    for idx, sample in enumerate(results["sample_issues"], start=1):
        payload = sample.get("payload", {})
        issue = payload.get("issue", {})
        labels = [l.get("name") if isinstance(l, dict) else l for l in issue.get("labels", [])]
        print(f"\n[Sample {idx}]")
        print(f"  Event ID   : {sample.get('id')}")
        print(f"  Created At : {sample.get('created_at')}")
        print(f"  Actor      : {sample.get('actor', {}).get('login')} (ID: {sample.get('actor', {}).get('id')})")
        print(f"  Repo       : {sample.get('repo', {}).get('name')} (ID: {sample.get('repo', {}).get('id')})")
        print(f"  Action     : {payload.get('action')}")
        print(f"  Issue #{issue.get('number')} Title : {issue.get('title')}")
        print(f"  Labels     : {labels}")

    return results


if __name__ == "__main__":
    run()
