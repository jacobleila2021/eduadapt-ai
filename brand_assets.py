"""Logo path for Alora AI (re-export for optional use)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
ASSETS_DIR = ROOT / "assets"
ALORA_LOGO = ASSETS_DIR / "alora_logo.png"

# Back-compat aliases — do not import these in app startup
EDUADAPT_LOGO = ALORA_LOGO
OMNILI_LOGO = ALORA_LOGO
