"""Data Quality reconciliation and accounting tracker.

Provides the DQCounter class to guarantee strict mathematical reconciliation:
rows_read == rows_kept + sum(dropped_per_reason).
"""

from collections import Counter
from typing import Any, Dict


class DQCounter:
    """Tracks rows through ingestion and transformation layers.

    Enforces that every row is accounted for either as kept or with an explicit drop reason.
    """

    def __init__(self) -> None:
        self.rows_read: int = 0
        self.rows_kept: int = 0
        self.dropped_by_reason: Counter[str] = Counter()

    def record_read(self, count: int = 1) -> None:
        """Increment count of raw rows read from source."""
        self.rows_read += count

    def record_kept(self, count: int = 1) -> None:
        """Increment count of valid rows kept for output layer."""
        self.rows_kept += count

    def record_drop(self, reason: str, count: int = 1) -> None:
        """Increment drop count for a specific reason code."""
        self.dropped_by_reason[reason] += count

    @property
    def total_dropped(self) -> int:
        """Calculate total number of dropped rows across all reasons."""
        return sum(self.dropped_by_reason.values())

    def reconciles(self) -> bool:
        """Return True if rows_read exactly matches rows_kept + total_dropped."""
        return self.rows_read == (self.rows_kept + self.total_dropped)

    def assert_reconciles(self) -> None:
        """Raise an AssertionError if reconciliation equation fails."""
        if not self.reconciles():
            difference = self.rows_read - (self.rows_kept + self.total_dropped)
            raise AssertionError(
                f"Data quality reconciliation failed! "
                f"rows_read ({self.rows_read}) != rows_kept ({self.rows_kept}) + "
                f"total_dropped ({self.total_dropped}). Discrepancy: {difference} rows."
            )

    def to_dict(self) -> Dict[str, Any]:
        """Export metrics to dictionary for reporting and JSON serialization."""
        return {
            "rows_read": self.rows_read,
            "rows_kept": self.rows_kept,
            "total_dropped": self.total_dropped,
            "reconciled": self.reconciles(),
            "dropped_by_reason": dict(self.dropped_by_reason),
        }
