"""Unit tests for the Clean Layer transformation and data quality rules."""

import json
from pathlib import Path
import pyarrow.dataset as ds
import pytest

from src.common.config import PROJECT_ROOT
from src.common.dq import DQCounter
from src.transform.clean import clean_file, hash_actor, validate_and_extract_row
from src.transform.reasons import (
    DROP_BAD_TIMESTAMP,
    DROP_BOT,
    DROP_CORRUPT_JSON,
    DROP_DUPLICATE_EVENT_ID,
    DROP_EMPTY_TITLE,
    DROP_MISSING_PAYLOAD_ISSUE,
    DROP_UNSUPPORTED_TYPE,
)

FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "sample_events.jsonl"


def test_fixture_rules_reconciliation_and_reasons(tmp_path: Path) -> None:
    """Verify that all 20 fixture lines are cleanly classified with exact reason codes."""
    dq = DQCounter()
    seen_ids = set()

    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    assert len(lines) == 20, f"Expected 20 lines in fixture, got {len(lines)}"

    kept_records = []
    for line in lines:
        rec = validate_and_extract_row(line, seen_ids, dq)
        if rec:
            kept_records.append(rec)

    # Reconciles strictly: rows_read == rows_kept + total_dropped
    dq.assert_reconciles()
    assert dq.rows_read == 20
    assert dq.rows_kept == 11
    assert dq.total_dropped == 9

    # Verify each expected drop reason code fired
    drops = dq.dropped_by_reason
    assert drops[DROP_BOT] == 2
    assert drops[DROP_EMPTY_TITLE] == 2
    assert drops[DROP_DUPLICATE_EVENT_ID] == 1
    assert drops[DROP_MISSING_PAYLOAD_ISSUE] == 1
    assert drops[DROP_BAD_TIMESTAMP] == 1
    assert drops[DROP_UNSUPPORTED_TYPE] == 1
    assert drops[DROP_CORRUPT_JSON] == 1


def test_actor_pseudonymisation() -> None:
    """Verify that actor logins are converted to non-reversible SHA-256 hashes."""
    login = "AliceCoder"
    h1 = hash_actor(login)
    h2 = hash_actor("alicecoder")  # Case insensitive
    h3 = hash_actor("BobDev")

    assert len(h1) == 64
    assert h1 == h2
    assert h1 != h3
    assert login.lower() not in h1


def test_clean_file_writes_valid_parquet(tmp_path: Path) -> None:
    """Verify that clean_file writes partitioned Parquet readable by PyArrow."""
    dq = DQCounter()
    seen_ids = set()
    clean_file(FIXTURE_PATH, tmp_path, seen_ids, dq, batch_size=10)

    dq.assert_reconciles()
    assert dq.rows_kept == 11

    # Read back partitioned dataset with PyArrow
    dataset = ds.dataset(tmp_path, format="parquet", partitioning="hive")
    table = dataset.to_table()

    assert table.num_rows == 11
    assert "event_id" in table.column_names
    assert "actor_hash" in table.column_names
    assert "event_type" in table.column_names


def test_idempotent_double_run(tmp_path: Path) -> None:
    """Verify that running the clean job twice produces identical, non-duplicated output."""
    dq1 = DQCounter()
    seen1 = set()
    clean_file(FIXTURE_PATH, tmp_path, seen1, dq1)
    dq1.assert_reconciles()

    count_run1 = ds.dataset(tmp_path, format="parquet", partitioning="hive").to_table().num_rows
    assert count_run1 == 11

    # Second run with same input and clean seen_ids (simulating fresh DAG run)
    dq2 = DQCounter()
    seen2 = set()
    clean_file(FIXTURE_PATH, tmp_path, seen2, dq2)
    dq2.assert_reconciles()

    count_run2 = ds.dataset(tmp_path, format="parquet", partitioning="hive").to_table().num_rows
    # Must overwrite or remain identical, never duplicate rows to 22
    assert count_run2 == 11
