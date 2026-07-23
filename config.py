"""
Configuration constants for Alora AI.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

APP_NAME = "Alora AI"
APP_TAGLINE = "Built for Learning. Powered by Intelligence."

# Alora + EduAdapt hybrid palette (proven readability)
COLOR_DEEP_NAVY = "#041B4D"
COLOR_TEAL = "#008C95"
COLOR_ELECTRIC_CYAN = "#14D9E5"
COLOR_BRIGHT_AQUA = "#22F0FF"
COLOR_SILVER = "#C0C0C0"
COLOR_WHITE = "#FFFFFF"
COLOR_PAGE_BG = "#FFFFFF"
COLOR_TEXT = "#041B4D"

COLOR_DARK_BLUE = COLOR_DEEP_NAVY

PROJECT_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "assets"

MANUAL_TIME_HOURS = 4
EDUADAPT_TIME_MINUTES = 2
TIME_SAVED_PERCENT = 95

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TIMEOUT_SECONDS = float(os.getenv("OPENAI_TIMEOUT_SECONDS", "90"))
OPENAI_MAX_RETRIES = int(os.getenv("OPENAI_MAX_RETRIES", "2"))

# Picture Words illustrations: off (use flowcharts) | pollinations | openai
IMAGE_PROVIDER = os.getenv("IMAGE_PROVIDER", "off").strip().lower()

# ULI Milestone 2.3 — pipeline wiring (default OFF for backward compatibility)
ENABLE_ULI_PIPELINE = os.getenv("ENABLE_ULI_PIPELINE", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

# Lesson Composition Engine (LCE) 1.0 — final educational author before ULIQE/render
# Default ON: compose premium lessons from ULI/SIF/UVIE; set ENABLE_LCE_PIPELINE=false to skip.
ENABLE_LCE_PIPELINE = os.getenv("ENABLE_LCE_PIPELINE", "true").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

KNOWLEDGE_DATA_DIR = PROJECT_ROOT / "data" / "knowledge"
CHROMA_DIR = KNOWLEDGE_DATA_DIR / "chroma"
PILOT_GRADE = "8"
PILOT_SUBJECT = "Science"
PILOT_BOARD = "CBSE"

MAX_LESSON_CHARS = 50000
MAX_CHUNK_CHARS = 14000
