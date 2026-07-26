"""Domain topic detection and prerequisite hints (curriculum-agnostic)."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.taxonomy import (
    concept_graph_from_uli as _concept_graph,
    detect_domains as _detect_domains,
    prerequisite_hints as _prerequisite_hints,
)

DOMAIN_MARKERS: dict[str, tuple[str, ...]] = {
    "arithmetic": ("add", "subtract", "multiply", "divide", "fraction", "decimal", "percent", "place value"),
    "algebra": ("equation", "variable", "expression", "solve for", "linear", "quadratic", "polynomial", "inequalit"),
    "geometry": ("triangle", "circle", "angle", "perimeter", "area", "volume", "polygon", "congruen", "similar"),
    "trigonometry": ("sin", "cos", "tan", "sine", "cosine", "tangent", "trig"),
    "calculus": ("derivative", "integral", "differentiate", "limit", "dy/dx", "d/dx"),
    "statistics": ("mean", "median", "mode", "standard deviation", "histogram", "frequency"),
    "probability": ("probability", "outcome", "sample space", "permutation", "combination"),
    "number_systems": ("integer", "rational", "irrational", "real number", "natural number", "whole number"),
}

PREREQ_EDGES: tuple[tuple[str, str], ...] = (
    ("arithmetic", "algebra"),
    ("number_systems", "algebra"),
    ("algebra", "trigonometry"),
    ("geometry", "trigonometry"),
    ("algebra", "calculus"),
    ("trigonometry", "calculus"),
    ("arithmetic", "statistics"),
    ("arithmetic", "probability"),
    ("statistics", "probability"),
)


def detect_domains(text: str) -> list[dict[str, Any]]:
    return _detect_domains(text, DOMAIN_MARKERS)


def prerequisite_hints(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _prerequisite_hints(
        domains,
        PREREQ_EDGES,
        provenance="mathematics_intelligence.domain_prereqs",
    )


def concept_graph_from_uli(uli: Any, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _concept_graph(
        uli,
        domains,
        PREREQ_EDGES,
        domain_node_type="math_domain",
        provenance="mathematics_intelligence",
    )
