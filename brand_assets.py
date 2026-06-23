"""Logo paths — separate module so Streamlit Cloud never misses config exports."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
EDUADAPT_LOGO = ASSETS_DIR / "eduadapt_logo.png"
OMNILI_LOGO = ASSETS_DIR / "omnili_logo.png"
