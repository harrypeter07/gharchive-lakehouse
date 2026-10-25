"""Unit tests for the Data Quality counter and reconciliation helper."""

import pytest
from src.common.dq import DQCounter
from src.transform.reasons import DROP_BOT, DROP_EMPTY_TITLE, DROP_DUPLICATE_EVENT_ID


def test_dq_counter_reconciles_cleanly() -> None:
    """Verify that DQCounter successfully reconciles when all rows are accounted for."""
    counter = DQCounter()
    counter.record_read(10)
    counter.record_kept(6)
    counter.record_drop(DROP_BOT, 2)
    counter.record_drop(DROP_EMPTY_TITLE, 1)
    counter.record_drop(DROP_DUPLICATE_EVENT_ID, 1)

    assert counter.rows_read == 10
    assert counter.rows_kept == 6
    assert counter.total_dropped == 4
    assert counter.reconciles() is True

    # Should not raise any exception
    counter.assert_reconciles()

    summary = counter.to_dict()
    assert summary["rows_read"] == 10
    assert summary["rows_kept"] == 6
    assert summary["total_dropped"] == 4
    assert summary["reconciled"] is True
    assert summary["dropped_by_reason"][DROP_BOT] == 2


def test_dq_counter_fails_loudly_on_mismatch() -> None:
    """Verify that assert_reconciles raises AssertionError if rows are silently dropped."""
    counter = DQCounter()
    counter.record_read(10)
    counter.record_kept(6)
    # Only 3 drops recorded out of 4 unaccounted rows
    counter.record_drop(DROP_BOT, 3)

    assert counter.reconciles() is False
    with pytest.raises(AssertionError) as exc_info:
        counter.assert_reconciles()

    assert "Data quality reconciliation failed" in str(exc_info.value)
    assert "Discrepancy: 1 rows" in str(exc_info.value)
