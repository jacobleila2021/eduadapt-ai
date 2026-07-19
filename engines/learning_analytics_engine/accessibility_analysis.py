"""Accessibility analytics — wraps AIE signals (no medical inferences)."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.curriculum_analysis import accessibility_analysis as _a11y


def accessibility_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    return _a11y(sources)
