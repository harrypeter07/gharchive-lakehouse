"""Download 24 hourly event files for a given date from GH Archive.

Implements DNS fallback, socket timeouts, retries, resume caching,
strict gzip stream validation (no truncated files), and manifest generation.
"""

import argparse
import concurrent.futures
import datetime
import gzip
import json
import logging
import socket
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

from src.common.config import RAW_DATA_DIR

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

socket.setdefaulttimeout(45)

_ORIG_GETADDRINFO = socket.getaddrinfo
_FALLBACK_IPS = ["104.21.46.175", "172.67.168.206"]


def _resilient_getaddrinfo(host, port, *args, **kwargs):
    try:
        return _ORIG_GETADDRINFO(host, port, *args, **kwargs)
    except socket.gaierror:
        if host == "data.gharchive.org":
            for ip in _FALLBACK_IPS:
                try:
                    return _ORIG_GETADDRINFO(ip, port, *args, **kwargs)
                except Exception:
                    continue
        raise


socket.getaddrinfo = _resilient_getaddrinfo
USER_AGENT = "gharchive-lakehouse/1.0 (educational research)"


def verify_gzip_integrity(file_path: Path) -> bool:
    """Verify that a gzip file is non-empty and decompresses without EOF errors."""
    if not file_path.exists() or file_path.stat().st_size < 1024:
        return False
    try:
        with gzip.open(file_path, "rb") as gz:
            while chunk := gz.read(4 * 1024 * 1024):
                pass
        return True
    except Exception:
        return False


def fetch_hour_file(
    date_str: str,
    hour: int,
    output_dir: Path,
    max_retries: int = 5,
    polite_pause: float = 0.5,
) -> Dict[str, Any]:
    """Download a single hourly compressed JSON archive file with strict verification."""
    filename = f"{date_str}-{hour}.json.gz"
    dest_path = output_dir / filename
    temp_path = output_dir / f"{filename}.tmp"
    url = f"https://data.gharchive.org/{filename}"

    if dest_path.exists() and verify_gzip_integrity(dest_path):
        file_size = dest_path.stat().st_size
        logger.info("Hour %02d verified in cache: %s (%d bytes)", hour, filename, file_size)
        return {
            "hour": hour,
            "filename": filename,
            "bytes": file_size,
            "status": "cached",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
    elif dest_path.exists():
        logger.warning("Hour %02d existing file is corrupt/truncated (%d bytes). Removing.", hour, dest_path.stat().st_size)
        dest_path.unlink(missing_ok=True)

    logger.info("Hour %02d downloading: %s ...", hour, url)
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=30) as response, open(temp_path, "wb") as out_f:
                content_len_header = response.headers.get("Content-Length")
                expected_bytes = int(content_len_header) if content_len_header else None

                downloaded = 0
                while chunk := response.read(1024 * 1024):
                    out_f.write(chunk)
                    downloaded += len(chunk)

            if expected_bytes and downloaded != expected_bytes:
                raise IOError(f"Truncated download: got {downloaded} bytes, expected {expected_bytes}")

            if not verify_gzip_integrity(temp_path):
                raise IOError(f"Corrupt gzip stream in temporary file ({temp_path.stat().st_size} bytes)")

            temp_path.replace(dest_path)
            file_size = dest_path.stat().st_size
            time.sleep(polite_pause)
            logger.info("Hour %02d complete and verified: %s (%d bytes)", hour, filename, file_size)
            return {
                "hour": hour,
                "filename": filename,
                "bytes": file_size,
                "status": "downloaded",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            }
        except Exception as err:
            logger.warning("Attempt %d failed for hour %d: %s", attempt, hour, err)
            if temp_path.exists():
                temp_path.unlink(missing_ok=True)
            if attempt < max_retries:
                time.sleep(3.0 * attempt)

    logger.error("Failed to download and verify hour %d after %d attempts", hour, max_retries)
    return {
        "hour": hour,
        "filename": filename,
        "bytes": 0,
        "status": "failed",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def write_manifest(manifest_path: Path, manifest_data: Dict[str, Any]) -> None:
    """Atomically write download manifest to disk."""
    temp_manifest = manifest_path.with_suffix(".tmp")
    with open(temp_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    temp_manifest.replace(manifest_path)
    logger.info("Manifest written to %s", manifest_path)


def download_day(
    date_str: str,
    output_dir: Optional[Path] = None,
    hours: Optional[List[int]] = None,
    max_workers: int = 2,
) -> Dict[str, Any]:
    """Download all hourly files for a date and generate the manifest."""
    out_dir = output_dir or RAW_DATA_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    target_hours = sorted(hours if hours is not None else list(range(24)))

    file_entries_map: Dict[int, Dict[str, Any]] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_hour = {
            executor.submit(fetch_hour_file, date_str, h, out_dir): h
            for h in target_hours
        }
        for future in concurrent.futures.as_completed(future_to_hour):
            h = future_to_hour[future]
            try:
                result = future.result()
                file_entries_map[h] = result
            except Exception as err:
                logger.error("Unexpected error for hour %d: %s", h, err)
                file_entries_map[h] = {
                    "hour": h,
                    "filename": f"{date_str}-{h}.json.gz",
                    "bytes": 0,
                    "status": "failed",
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                }

    file_entries = [file_entries_map[h] for h in target_hours]
    missing_hours = [e["hour"] for e in file_entries if e["status"] == "failed"]
    total_bytes = sum(e["bytes"] for e in file_entries)

    manifest_data = {
        "date": date_str,
        "total_files": len([e for e in file_entries if e["status"] != "failed"]),
        "expected_files": len(target_hours),
        "total_bytes": total_bytes,
        "missing_hours": missing_hours,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "files": file_entries,
    }

    manifest_path = out_dir / "manifest.json"
    write_manifest(manifest_path, manifest_data)
    return manifest_data


def parse_args() -> argparse.Namespace:
    """Parse command line arguments for the downloader."""
    parser = argparse.ArgumentParser(description="Download GH Archive full day")
    parser.add_argument("--date", type=str, default="2024-06-10", help="Date in YYYY-MM-DD format")
    parser.add_argument("--output-dir", type=Path, default=RAW_DATA_DIR, help="Destination directory")
    parser.add_argument("--hours", type=int, nargs="*", default=None, help="Optional subset of hours (0-23)")
    parser.add_argument("--workers", type=int, default=2, help="Concurrent worker threads")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    download_day(args.date, args.output_dir, args.hours, args.workers)
