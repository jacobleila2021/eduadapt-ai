"""Intervention analysis — effectiveness tracking hooks."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.curriculum_analysis import intervention_analysis as _iv


def intervention_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    return _iv(sources)
