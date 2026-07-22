"""LAIE analytics metadata for UVIE diagram interactions."""

from __future__ import annotations

from typing import Any

from engines.universal_visual_intelligence.schemas import VisualSpec


def analytics_metadata(specs: list[VisualSpec]) -> dict[str, Any]:
    return {
        "owner": "LAIE",
        "interaction_events": [
            "diagram_open",
            "diagram_zoom",
            "timeline_navigate",
            "map_scaffold_open",
            "flowchart_expand",
            "concept_map_click",
        ],
        "visual_ids": [s.visual_id for s in specs[:12]],
        "sources": sorted({s.source for s in specs}),
        "placeholder_count": sum(1 for s in specs if s.placeholder),
        "deterministic_count": sum(1 for s in specs if s.deterministic and not s.placeholder),
        "provenance": "universal_visual_intelligence.analytics",
        "track": [
            "diagram_usage",
            "organiser_usage",
            "verified_visual_views",
        ],
    }
