"""Accessibility recommendations for chemistry (AIE owns application)."""

from __future__ import annotations

from typing import Any

from engines.chemistry_intelligence.pedagogy import accessibility_guidance

__all__ = ["accessibility_guidance", "chemistry_accessibility_for_uli"]


def chemistry_accessibility_for_uli(uli: Any) -> list[dict[str, Any]]:
    return accessibility_guidance(uli)
