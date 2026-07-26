"""LAIE analytics metadata for CSIP."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.analytics import analytics_event_template


def analytics_metadata(
    domains: list[dict[str, Any]],
    misconceptions: list[dict[str, Any]],
) -> dict[str, Any]:
    return analytics_event_template(
        interaction_events=[
            "code_viewer_open",
            "trace_step",
            "algorithm_animate",
            "schema_explore",
            "topology_click",
            "debug_attempt",
        ],
        engagement_signals=[
            "programming_progress",
            "debugging_attempts",
            "algorithm_walkthrough_time",
        ],
        competency_ids=[d["domain"] for d in domains[:8]],
        misconception_ids=[m.get("misconception_id") for m in misconceptions[:8]],
        progression_markers=[
            "programming_progress",
            "debugging_attempts",
            "algorithm_understanding",
            "ai_concept_mastery",
            "database_competency",
            "networking_competency",
        ],
        intervention_recommendations=[
            {
                "misconception_id": m.get("misconception_id"),
                "strategy": m.get("correction_strategy"),
            }
            for m in misconceptions[:5]
        ],
        provenance="computer_science_intelligence.analytics",
    ) | {
        "track": [
            "programming_progress",
            "debugging_attempts",
            "algorithm_understanding",
            "ai_concept_mastery",
            "database_competency",
            "networking_competency",
        ],
    }
