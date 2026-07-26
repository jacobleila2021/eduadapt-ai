"""Accessibility facade — AIE owns application."""

from __future__ import annotations

from typing import Any

from engines.english_language_intelligence.pedagogy import accessibility_guidance

__all__ = ["accessibility_guidance", "english_accessibility_for_uli"]


def english_accessibility_for_uli(uli: Any) -> list[dict[str, Any]]:
    return accessibility_guidance(uli)
