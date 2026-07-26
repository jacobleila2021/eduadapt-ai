"""Competency helpers for social science domains."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.competencies import from_domain_prereqs


def competency_metadata(domains: list[dict[str, Any]], prereq: dict[str, Any]) -> dict[str, Any]:
    graph = from_domain_prereqs(
        domains,
        prereq,
        provenance="social_science_intelligence.competencies",
    )
    graph["strands"] = [
        "historical_reasoning",
        "geographic_reasoning",
        "civic_reasoning",
        "economic_reasoning",
        "source_analysis",
        "spatial_thinking",
    ]
    return graph
