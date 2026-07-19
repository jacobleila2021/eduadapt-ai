"""Recommendation facade (re-exports accommodations.generate_recommendations)."""

from __future__ import annotations

from engines.accessibility_intelligence_engine.accommodations import generate_recommendations

__all__ = ["generate_recommendations"]
