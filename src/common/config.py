"""Project configuration and path definitions.

Centralises file paths, random seeds, and global constants to avoid magic numbers.
"""

from pathlib import Path

# Base Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "clean"
CURATED_DATA_DIR = DATA_DIR / "curated"
CACHE_DIR = DATA_DIR / "cache"

# Ensure runtime directories exist
for directory in (RAW_DATA_DIR, CLEAN_DATA_DIR, CURATED_DATA_DIR, CACHE_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# Random Seed for reproducibility
GLOBAL_SEED = 42

# GH Archive sample target
SAMPLE_DATE_HOUR = "2024-06-10-15"
SAMPLE_URL = f"https://data.gharchive.org/{SAMPLE_DATE_HOUR}.json.gz"
