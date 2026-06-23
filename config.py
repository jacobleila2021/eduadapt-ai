"""
Configuration constants for EduAdapt AI.
Centralizes colors, timing estimates, and API settings.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from the project folder (reliable path)
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=True)

# --- Brand colors (Omnili / EduAdapt palette) ---
COLOR_DEEP_NAVY = "#041B4D"
COLOR_ELECTRIC_CYAN = "#14D9E5"
COLOR_BRIGHT_AQUA = "#22F0FF"
COLOR_SILVER = "#C0C0C0"
COLOR_WHITE = "#FFFFFF"

# Legacy aliases used across exporters
COLOR_DARK_BLUE = COLOR_DEEP_NAVY
COLOR_TEAL = COLOR_ELECTRIC_CYAN

PROJECT_ROOT = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_ROOT / "assets"
EDUADAPT_LOGO = ASSETS_DIR / "eduadapt_logo.png"
OMNILI_LOGO = ASSETS_DIR / "omnili_logo.png"

# --- Time-saved sidebar metrics ---
MANUAL_TIME_HOURS = 4
EDUADAPT_TIME_MINUTES = 2
TIME_SAVED_PERCENT = 95

# --- OpenAI settings ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Maximum characters kept in excerpt (full doc analyzed via chunking in lesson_processor)
MAX_LESSON_CHARS = 50000
MAX_CHUNK_CHARS = 14000
