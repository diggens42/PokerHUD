"""Global configuration for PokerHUD."""
from __future__ import annotations

from pathlib import Path

APP_NAME = "PokerHUD"

BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / "resources"
TESSDATA_DIR = RESOURCES_DIR / "tessdata"
TABLE_TEMPLATES_DIR = RESOURCES_DIR / "table_templates"
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

CAPTURE_INTERVAL_MS = 500
OCR_LANG = "eng"
OCR_PSM_SINGLE_LINE = 7
OCR_PSM_SINGLE_WORD = 8

DEFAULT_TESSERACT_PATH = ""

DB_PATH = DATA_DIR / "pokerhud.sqlite3"

DEBUG_SAVE_CAPTURES = False
DEBUG_CAPTURE_DIR = BASE_DIR / "captures"
