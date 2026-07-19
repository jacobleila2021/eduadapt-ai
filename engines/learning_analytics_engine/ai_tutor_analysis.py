"""AI Tutor analytics."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.curriculum_analysis import ai_tutor_analysis as _tutor


def ai_tutor_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    return _tutor(sources)
