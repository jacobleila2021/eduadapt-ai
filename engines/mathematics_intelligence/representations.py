"""Multiple-representation plans (CRA + verbal/tabular/graphical)."""

from __future__ import annotations

from typing import Any

from engines.mathematics_intelligence.visualizations import representation_plan, recommend_visuals_for_text

__all__ = ["representation_plan", "recommend_visuals_for_text", "build_representation_bundle"]


def build_representation_bundle(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "plan": representation_plan(domains),
        "recommended_visuals": recommend_visuals_for_text(text),
        "provenance": "mathematics_intelligence.representations",
    }
