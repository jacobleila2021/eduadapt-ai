"""Competency helpers for computer science domains."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.competencies import from_domain_prereqs


def competency_metadata(domains: list[dict[str, Any]], prereq: dict[str, Any]) -> dict[str, Any]:
    graph = from_domain_prereqs(
        domains,
        prereq,
        provenance="computer_science_intelligence.competencies",
    )
    graph["strands"] = [
        "computational_thinking",
        "programming",
        "algorithms_data_structures",
        "systems_networking",
        "data_and_databases",
        "cybersecurity_digital_citizenship",
        "ai_literacy",
    ]
    return graph
