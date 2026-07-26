"""Assessment / accessibility facades for CEIP."""

from __future__ import annotations

from typing import Any

from engines.commerce_economics_intelligence.pedagogy import (
    accessibility_guidance,
    assessment_hints,
    revision_summary,
)

__all__ = [
    "assessment_hints",
    "revision_summary",
    "accessibility_guidance",
    "commerce_economics_assessment_hints",
    "commerce_economics_accessibility_for_uli",
]


def commerce_economics_assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return assessment_hints(uli, domains)


def commerce_economics_accessibility_for_uli(uli: Any) -> list[dict[str, Any]]:
    return accessibility_guidance(uli)
