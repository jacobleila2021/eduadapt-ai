"""Knowledge Layer paths."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SEED_DIR = Path(__file__).resolve().parent / "seed"
DATA_DIR = PROJECT_ROOT / "data" / "knowledge"
CHROMA_DIR = DATA_DIR / "chroma"
INGEST_DIR = DATA_DIR / "ingested"
