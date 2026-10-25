"""Unit tests for GH Archive download manifest integrity.

Verifies that the manifest file exists, contains all 24 hourly entries,
and correctly records file size and download status.
"""

import json
from pathlib import Path
from src.common.config import RAW_DATA_DIR


def test_manifest_structure_and_coverage() -> None:
    """Verify that manifest.json has valid structure and reports all 24 hours."""
    manifest_path = RAW_DATA_DIR / "manifest.json"
    assert manifest_path.exists(), f"Manifest file missing at {manifest_path}"

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "date" in data, "Manifest missing 'date' field"
    assert "total_files" in data, "Manifest missing 'total_files' field"
    assert "total_bytes" in data, "Manifest missing 'total_bytes' field"
    assert "files" in data, "Manifest missing 'files' field"
    assert "missing_hours" in data, "Manifest missing 'missing_hours' field"

    files = data["files"]
    assert len(files) == 24, f"Expected 24 hourly file records in manifest, found {len(files)}"

    recorded_hours = {entry["hour"] for entry in files}
    expected_hours = set(range(24))
    assert recorded_hours == expected_hours, f"Hours do not match 0..23: {recorded_hours ^ expected_hours}"

    successful_files = [entry for entry in files if entry["status"] in ("downloaded", "cached")]
    assert len(successful_files) + len(data["missing_hours"]) == 24
