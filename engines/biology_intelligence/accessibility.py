"""Accessibility recommendations for biology (AIE owns application)."""

from __future__ import annotations

from typing import Any

from engines.biology_intelligence.pedagogy import accessibility_guidance

__all__ = ["accessibility_guidance", "biology_accessibility_for_uli"]


def biology_accessibility_for_uli(uli: Any) -> list[dict[str, Any]]:
    return accessibility_guidance(uli)
