"""Assessment metadata facade for AME."""

from __future__ import annotations

from typing import Any

from engines.english_language_intelligence.pedagogy import assessment_hints, revision_summary

__all__ = ["assessment_hints", "revision_summary", "english_assessment_hints"]


def english_assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return assessment_hints(uli, domains)
