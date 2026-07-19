"""Curriculum Intelligence Engine package — academic brain of Alora AI."""

from engines.curriculum_intelligence_engine.intelligence import (
    analyze_lesson_context,
    compare_boards,
    ensure_indexed,
    get_runtime,
    search,
)
from engines.curriculum_intelligence_engine import service as cie_api

__all__ = [
    "analyze_lesson_context",
    "compare_boards",
    "ensure_indexed",
    "get_runtime",
    "search",
    "cie_api",
]
