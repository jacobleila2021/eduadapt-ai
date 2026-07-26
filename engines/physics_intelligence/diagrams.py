"""Diagram recommendation facade (aliases visualizations for package contract)."""

from __future__ import annotations

from typing import Any

from engines.physics_intelligence.visualizations import recommend_visuals_for_text, representation_plan

__all__ = ["recommend_visuals_for_text", "representation_plan", "diagram_bundle"]


def diagram_bundle(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "plan": representation_plan(domains),
        "recommended_diagrams": recommend_visuals_for_text(text),
        "provenance": "physics_intelligence.diagrams",
    }
