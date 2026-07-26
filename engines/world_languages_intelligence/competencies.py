"""Competency helpers for world languages domains."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.competencies import from_domain_prereqs


def competency_metadata(domains: list[dict[str, Any]], prereq: dict[str, Any]) -> dict[str, Any]:
    graph = from_domain_prereqs(
        domains,
        prereq,
        provenance="world_languages_intelligence.competencies",
    )
    graph["strands"] = [
        "listening",
        "speaking",
        "reading",
        "writing",
        "vocabulary",
        "grammar",
        "pronunciation",
        "intercultural",
    ]
    return graph
