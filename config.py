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

# --- Brand colors (EdTech palette) ---
COLOR_DARK_BLUE = "#0B2E59"
COLOR_TEAL = "#008C95"
COLOR_SILVER = "#C0C0C0"
COLOR_WHITE = "#FFFFFF"

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
