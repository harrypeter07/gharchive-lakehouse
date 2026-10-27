"""Project configuration and path definitions.

Centralises file paths, environment secrets, random seeds, and global constants.
Loads environment variables safely from .env via python-dotenv.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base Directory Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "clean"
CURATED_DATA_DIR = DATA_DIR / "curated"
CACHE_DIR = DATA_DIR / "cache"

# Ensure runtime directories exist
for directory in (RAW_DATA_DIR, CLEAN_DATA_DIR, CURATED_DATA_DIR, CACHE_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# Configuration Constants
GLOBAL_SEED = 42
DEFAULT_DATE = os.getenv("GHARCHIVE_DATE", "2024-06-10")

# Allowed event types for Clean Layer (P1.3)
ALLOWED_EVENT_TYPES = (
    "IssuesEvent",
    "PullRequestEvent",
    "PushEvent",
    "WatchEvent",
    "ForkEvent",
    "IssueCommentEvent",
)

# Salt for actor pseudonymisation (salted SHA-256)
# Fallback to dev salt if not set, but production requires setting ACTOR_HASH_SALT in .env
ACTOR_HASH_SALT = os.getenv("ACTOR_HASH_SALT") or os.getenv("ACTOR_SALT") or "dev_salt_only_change_in_env"

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Small CPU lab classifier defaults
DL_MAX_LEN = 50
DL_BATCH_SIZE = 64
DL_LEARNING_RATE = 0.001
DL_EPOCHS = 8
DL_CPU_THREADS = 2
DL_LABELS = ("bug", "enhancement", "documentation", "question")
