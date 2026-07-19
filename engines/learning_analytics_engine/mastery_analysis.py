"""Mastery analytics — wraps AME/ALE mastery signals."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.curriculum_analysis import mastery_analysis as _mastery


def mastery_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    return _mastery(sources)
