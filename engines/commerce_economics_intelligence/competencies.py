"""Competency helpers for commerce & economics domains."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.competencies import from_domain_prereqs


def competency_metadata(domains: list[dict[str, Any]], prereq: dict[str, Any]) -> dict[str, Any]:
    graph = from_domain_prereqs(
        domains,
        prereq,
        provenance="commerce_economics_intelligence.competencies",
    )
    graph["strands"] = [
        "accounting",
        "economic_reasoning",
        "business_decision_making",
        "financial_literacy",
        "entrepreneurship",
        "marketing_management",
    ]
    return graph
