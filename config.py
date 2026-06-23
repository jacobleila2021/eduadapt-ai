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

MAX_LESSON_CHARS = 50000
MAX_CHUNK_CHARS = 14000
