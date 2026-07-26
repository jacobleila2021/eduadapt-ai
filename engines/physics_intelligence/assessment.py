"""Assessment metadata hints for AME (AME owns item generation)."""

from __future__ import annotations

from typing import Any

from engines.physics_intelligence.pedagogy import assessment_hints

__all__ = ["assessment_hints", "physics_assessment_hints_for_uli"]


def physics_assessment_hints_for_uli(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return assessment_hints(uli, domains)
