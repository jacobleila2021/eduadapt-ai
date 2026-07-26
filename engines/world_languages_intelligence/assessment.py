"""Assessment / accessibility facades for WLIP."""

from __future__ import annotations

from typing import Any

from engines.world_languages_intelligence.pedagogy import (
    accessibility_guidance,
    assessment_hints,
    revision_summary,
)

__all__ = [
    "assessment_hints",
    "revision_summary",
    "accessibility_guidance",
    "world_languages_assessment_hints",
    "world_languages_accessibility_for_uli",
]


def world_languages_assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return assessment_hints(uli, domains)


def world_languages_accessibility_for_uli(uli: Any) -> list[dict[str, Any]]:
    return accessibility_guidance(uli)
