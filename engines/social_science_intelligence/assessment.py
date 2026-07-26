"""Assessment / accessibility facades."""

from __future__ import annotations

from typing import Any

from engines.social_science_intelligence.pedagogy import (
    accessibility_guidance,
    assessment_hints,
    revision_summary,
)

__all__ = [
    "assessment_hints",
    "revision_summary",
    "accessibility_guidance",
    "social_science_assessment_hints",
    "social_science_accessibility_for_uli",
]


def social_science_assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return assessment_hints(uli, domains)


def social_science_accessibility_for_uli(uli: Any) -> list[dict[str, Any]]:
    return accessibility_guidance(uli)
