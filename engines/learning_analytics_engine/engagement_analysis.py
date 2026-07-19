"""Engagement analytics — reader + gamification + ALE consistency."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.curriculum_analysis import engagement_analysis as _eng


def engagement_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    return _eng(sources)
