"""Domain modules — thin pedagogical facets over shared domain detection."""

from __future__ import annotations

from typing import Any

from engines.mathematics_intelligence.domains import detect_domains


def _domain_view(text: str, domain: str) -> dict[str, Any]:
    hits = [d for d in detect_domains(text) if d["domain"] == domain]
    return {
        "domain": domain,
        "active": bool(hits),
        "markers": hits[0]["markers"] if hits else [],
        "score": hits[0]["score"] if hits else 0,
        "provenance": f"mathematics_intelligence.{domain}",
    }


def analyse_arithmetic(text: str) -> dict[str, Any]:
    return _domain_view(text, "arithmetic")


def analyse_algebra(text: str) -> dict[str, Any]:
    return _domain_view(text, "algebra")


def analyse_geometry(text: str) -> dict[str, Any]:
    return _domain_view(text, "geometry")


def analyse_trigonometry(text: str) -> dict[str, Any]:
    return _domain_view(text, "trigonometry")


def analyse_calculus(text: str) -> dict[str, Any]:
    return _domain_view(text, "calculus")


def analyse_statistics(text: str) -> dict[str, Any]:
    return _domain_view(text, "statistics")


def analyse_probability(text: str) -> dict[str, Any]:
    return _domain_view(text, "probability")


def analyse_number_systems(text: str) -> dict[str, Any]:
    return _domain_view(text, "number_systems")
