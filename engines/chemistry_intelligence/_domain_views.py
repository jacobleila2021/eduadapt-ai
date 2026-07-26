"""Domain facet helpers for chemistry topics."""

from __future__ import annotations

from typing import Any

from engines.chemistry_intelligence.domains import detect_domains


def _domain_view(text: str, domain: str) -> dict[str, Any]:
    hits = [d for d in detect_domains(text) if d["domain"] == domain]
    return {
        "domain": domain,
        "active": bool(hits),
        "markers": hits[0]["markers"] if hits else [],
        "score": hits[0]["score"] if hits else 0,
        "provenance": f"chemistry_intelligence.{domain}",
    }


def analyse_atomic_structure(text: str) -> dict[str, Any]:
    return _domain_view(text, "atomic_structure")


def analyse_periodic_table(text: str) -> dict[str, Any]:
    return _domain_view(text, "periodic_table")


def analyse_chemical_bonding(text: str) -> dict[str, Any]:
    return _domain_view(text, "chemical_bonding")


def analyse_reactions(text: str) -> dict[str, Any]:
    return _domain_view(text, "reactions")


def analyse_stoichiometry(text: str) -> dict[str, Any]:
    return _domain_view(text, "stoichiometry")


def analyse_acids_bases(text: str) -> dict[str, Any]:
    return _domain_view(text, "acids_bases")


def analyse_organic(text: str) -> dict[str, Any]:
    return _domain_view(text, "organic")


def analyse_inorganic(text: str) -> dict[str, Any]:
    return _domain_view(text, "inorganic")


def analyse_electrochemistry(text: str) -> dict[str, Any]:
    return _domain_view(text, "electrochemistry")


def analyse_thermochemistry(text: str) -> dict[str, Any]:
    return _domain_view(text, "thermochemistry")


def analyse_kinetics(text: str) -> dict[str, Any]:
    return _domain_view(text, "kinetics")


def analyse_equilibrium(text: str) -> dict[str, Any]:
    return _domain_view(text, "equilibrium")


def analyse_laboratory(text: str) -> dict[str, Any]:
    return _domain_view(text, "laboratory")
