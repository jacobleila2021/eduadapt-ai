"""Physics domain detection and prerequisite hints (curriculum-agnostic)."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.taxonomy import (
    concept_graph_from_uli as _concept_graph,
    detect_domains as _detect_domains,
    prerequisite_hints as _prerequisite_hints,
)

DOMAIN_MARKERS: dict[str, tuple[str, ...]] = {
    "mechanics": ("mechanic", "newton", "statics", "dynamics", "rigid body"),
    "motion": ("velocity", "acceleration", "displacement", "kinematics", "speed", "motion"),
    "forces": ("force", "friction", "tension", "normal force", "net force", "free-body", "fbd"),
    "energy": ("kinetic energy", "potential energy", "work-energy", "conservation of energy", "joule"),
    "momentum": ("momentum", "impulse", "collision", "conservation of momentum"),
    "electricity": ("current", "voltage", "resistance", "ohm", "circuit", "ampere", "coulomb"),
    "magnetism": ("magnetic", "electromagnet", "faraday", "flux", "solenoid"),
    "optics": ("reflection", "refraction", "lens", "mirror", "ray diagram", "focal"),
    "waves": ("wavelength", "frequency", "amplitude", "sound wave", "oscillat", "period"),
    "thermodynamics": ("heat", "temperature", "thermal", "entropy", "conduction", "convection"),
    "measurements": ("si unit", "measurement", "uncertainty", "significant figure", "vernier", "error"),
}

PREREQ_EDGES: tuple[tuple[str, str], ...] = (
    ("measurements", "motion"),
    ("motion", "forces"),
    ("forces", "mechanics"),
    ("motion", "energy"),
    ("forces", "energy"),
    ("motion", "momentum"),
    ("forces", "momentum"),
    ("energy", "thermodynamics"),
    ("electricity", "magnetism"),
    ("waves", "optics"),
    ("measurements", "electricity"),
    ("measurements", "waves"),
)


def detect_domains(text: str) -> list[dict[str, Any]]:
    return _detect_domains(text, DOMAIN_MARKERS)


def prerequisite_hints(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _prerequisite_hints(
        domains,
        PREREQ_EDGES,
        provenance="physics_intelligence.domain_prereqs",
    )


def concept_graph_from_uli(uli: Any, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _concept_graph(
        uli,
        domains,
        PREREQ_EDGES,
        domain_node_type="physics_domain",
        provenance="physics_intelligence",
    )
