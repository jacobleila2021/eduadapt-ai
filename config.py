"""
Configuration constants for EduAdapt AI.
Centralizes colors, timing estimates, and API settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from the project root explicitly.
# This is more reliable than relying on the current working directory.
ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)

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

# Maximum characters sent to the model (keeps costs predictable)
MAX_LESSON_CHARS = 12000

# Tab labels shown in the main content area
OUTPUT_TAB_LABELS = [
    "Original Lesson",
    "Dyslexia-Friendly",
    "ADHD-Friendly",
    "Simplified",
    "Advanced Learner",
    "English Language Learner",
    "Classroom Activities",
    "Teacher Notes",
]
