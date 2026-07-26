"""Accessibility recommendations for mathematics (AIE owns application)."""

from __future__ import annotations

from typing import Any

from engines.mathematics_intelligence.pedagogy import accessibility_guidance

__all__ = ["accessibility_guidance", "math_accessibility_for_uli"]


def math_accessibility_for_uli(uli: Any) -> list[dict[str, Any]]:
    return accessibility_guidance(uli)
