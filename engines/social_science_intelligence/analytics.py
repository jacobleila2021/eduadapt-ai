"""LAIE analytics metadata for SSIP."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.analytics import analytics_event_template


def analytics_metadata(
    domains: list[dict[str, Any]],
    misconceptions: list[dict[str, Any]],
    timelines: dict[str, Any],
    maps: dict[str, Any],
) -> dict[str, Any]:
    return analytics_event_template(
        interaction_events=[
            "timeline_open",
            "timeline_navigate",
            "map_click",
            "overlay_toggle",
            "source_annotate",
            "cause_effect_build",
        ],
        engagement_signals=["timeline_usage", "map_interactions", "source_analysis_time"],
        competency_ids=[d["domain"] for d in domains[:8]],
        misconception_ids=[m.get("misconception_id") for m in misconceptions[:8]],
        progression_markers=[
            "timeline_usage",
            "map_interactions",
            "source_analysis",
            "vocabulary_growth",
            "civic_reasoning",
            "historical_reasoning",
            "geographic_reasoning",
        ],
        intervention_recommendations=[
            {
                "misconception_id": m.get("misconception_id"),
                "strategy": m.get("correction_strategy"),
            }
            for m in misconceptions[:5]
        ],
        provenance="social_science_intelligence.analytics",
    ) | {
        "timeline_applicable": bool(timelines.get("applicable")),
        "map_applicable": bool(maps.get("applicable")),
        "track": [
            "timeline_usage",
            "map_interactions",
            "source_analysis",
            "vocabulary_growth",
            "civic_reasoning",
            "historical_reasoning",
            "geographic_reasoning",
        ],
    }
