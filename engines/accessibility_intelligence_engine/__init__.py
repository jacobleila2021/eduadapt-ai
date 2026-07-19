"""Accessibility Intelligence Engine package."""

from engines.accessibility_intelligence_engine.intelligence import (
    analyze_accessibility_context,
    ensure_indexed,
)
from engines.accessibility_intelligence_engine import service as aie_api

__all__ = [
    "analyze_accessibility_context",
    "ensure_indexed",
    "aie_api",
]
