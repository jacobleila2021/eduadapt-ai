"""Competency helpers for English literacy domains."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.competencies import from_domain_prereqs


def competency_metadata(domains: list[dict[str, Any]], prereq: dict[str, Any]) -> dict[str, Any]:
    graph = from_domain_prereqs(
        domains,
        prereq,
        provenance="english_language_intelligence.competencies",
    )
    graph["literacy_strands"] = [
        "reading",
        "writing",
        "speaking",
        "listening",
        "vocabulary",
        "grammar",
        "literature",
    ]
    return graph
