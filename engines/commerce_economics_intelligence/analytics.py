"""LAIE analytics metadata for CEIP."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.analytics import analytics_event_template


def analytics_metadata(
    domains: list[dict[str, Any]],
    misconceptions: list[dict[str, Any]],
) -> dict[str, Any]:
    return analytics_event_template(
        interaction_events=[
            "balance_sheet_open",
            "graph_explore",
            "canvas_edit",
            "decision_tree_step",
            "dashboard_filter",
            "workflow_step",
        ],
        engagement_signals=[
            "accounting_competency",
            "economic_reasoning",
            "business_decision_making",
        ],
        competency_ids=[d["domain"] for d in domains[:8]],
        misconception_ids=[m.get("misconception_id") for m in misconceptions[:8]],
        progression_markers=[
            "accounting_competency",
            "economic_reasoning",
            "business_decision_making",
            "financial_literacy_growth",
            "entrepreneurship_progress",
        ],
        intervention_recommendations=[
            {
                "misconception_id": m.get("misconception_id"),
                "strategy": m.get("correction_strategy"),
            }
            for m in misconceptions[:5]
        ],
        provenance="commerce_economics_intelligence.analytics",
    ) | {
        "track": [
            "accounting_competency",
            "economic_reasoning",
            "business_decision_making",
            "financial_literacy_growth",
            "entrepreneurship_progress",
        ],
    }
