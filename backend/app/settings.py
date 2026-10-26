"""Local paths and MVP quotas shared by the backend."""

from pathlib import Path

APP_NAME = "Document Scanner"
API_PREFIX = "/api/v1"

# Resolve from this file so launching from another directory keeps the same data.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIR / "scanner.sqlite3"
TEMP_DIR = DATA_DIR / "tmp"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_IMAGE_PIXELS = 16_000_000
MAX_PAGES_PER_SESSION = 20
