"""Domain facet helpers for biology topics."""

from __future__ import annotations

from typing import Any

from engines.biology_intelligence.domains import detect_domains


def _domain_view(text: str, domain: str) -> dict[str, Any]:
    hits = [d for d in detect_domains(text) if d["domain"] == domain]
    return {
        "domain": domain,
        "active": bool(hits),
        "markers": hits[0]["markers"] if hits else [],
        "score": hits[0]["score"] if hits else 0,
        "provenance": f"biology_intelligence.{domain}",
    }


def analyse_cell_biology(text: str) -> dict[str, Any]:
    return _domain_view(text, "cell_biology")


def analyse_human_biology(text: str) -> dict[str, Any]:
    return _domain_view(text, "human_biology")


def analyse_plant_biology(text: str) -> dict[str, Any]:
    return _domain_view(text, "plant_biology")


def analyse_genetics(text: str) -> dict[str, Any]:
    return _domain_view(text, "genetics")


def analyse_evolution(text: str) -> dict[str, Any]:
    return _domain_view(text, "evolution")


def analyse_ecology(text: str) -> dict[str, Any]:
    return _domain_view(text, "ecology")


def analyse_microbiology(text: str) -> dict[str, Any]:
    return _domain_view(text, "microbiology")


def analyse_anatomy(text: str) -> dict[str, Any]:
    return _domain_view(text, "anatomy")


def analyse_physiology(text: str) -> dict[str, Any]:
    return _domain_view(text, "physiology")


def analyse_taxonomy(text: str) -> dict[str, Any]:
    return _domain_view(text, "taxonomy")


def analyse_laboratory(text: str) -> dict[str, Any]:
    return _domain_view(text, "laboratory")


def analyse_biotechnology(text: str) -> dict[str, Any]:
    return _domain_view(text, "biotechnology")
