"""Domain facet helpers for physics topics."""

from __future__ import annotations

from typing import Any

from engines.physics_intelligence.domains import detect_domains


def _domain_view(text: str, domain: str) -> dict[str, Any]:
    hits = [d for d in detect_domains(text) if d["domain"] == domain]
    return {
        "domain": domain,
        "active": bool(hits),
        "markers": hits[0]["markers"] if hits else [],
        "score": hits[0]["score"] if hits else 0,
        "provenance": f"physics_intelligence.{domain}",
    }


def analyse_mechanics(text: str) -> dict[str, Any]:
    return _domain_view(text, "mechanics")


def analyse_motion(text: str) -> dict[str, Any]:
    return _domain_view(text, "motion")


def analyse_forces(text: str) -> dict[str, Any]:
    return _domain_view(text, "forces")


def analyse_energy(text: str) -> dict[str, Any]:
    return _domain_view(text, "energy")


def analyse_momentum(text: str) -> dict[str, Any]:
    return _domain_view(text, "momentum")


def analyse_electricity(text: str) -> dict[str, Any]:
    return _domain_view(text, "electricity")


def analyse_magnetism(text: str) -> dict[str, Any]:
    return _domain_view(text, "magnetism")


def analyse_optics(text: str) -> dict[str, Any]:
    return _domain_view(text, "optics")


def analyse_waves(text: str) -> dict[str, Any]:
    return _domain_view(text, "waves")


def analyse_thermodynamics(text: str) -> dict[str, Any]:
    return _domain_view(text, "thermodynamics")


def analyse_measurements(text: str) -> dict[str, Any]:
    return _domain_view(text, "measurements")
