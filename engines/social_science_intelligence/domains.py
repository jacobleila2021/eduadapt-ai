"""Social science domain detection — history/geography/civics/economics family."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.taxonomy import (
    concept_graph_from_uli as _concept_graph,
    detect_domains as _detect_domains,
    prerequisite_hints as _prerequisite_hints,
)

DOMAIN_MARKERS: dict[str, tuple[str, ...]] = {
    "history": (
        "history",
        "historical",
        "empire",
        "civilisation",
        "civilization",
        "chronology",
        "timeline",
        "dynasty",
        "revolution",
        "colony",
        "biography",
        "primary source",
        "secondary source",
    ),
    "geography": (
        "geography",
        "climate",
        "weather",
        "landform",
        "map",
        "latitude",
        "longitude",
        "population",
        "natural resource",
        "plateau",
        "river",
        "monsoon",
        "gis",
    ),
    "civics": (
        "civics",
        "constitution",
        "democracy",
        "citizenship",
        "rights",
        "duties",
        "election",
        "parliament",
        "rule of law",
        "fundamental rights",
    ),
    "political_science": (
        "political science",
        "governance",
        "public policy",
        "legislature",
        "judiciary",
        "executive",
        "federal",
        "state government",
    ),
    "economics": (
        "economics",
        "supply",
        "demand",
        "market",
        "inflation",
        "banking",
        "trade",
        "budget",
        "employment",
        "financial literacy",
        "gdp",
    ),
    "sociology": (
        "sociology",
        "community",
        "culture",
        "diversity",
        "social institution",
        "family",
        "global citizenship",
    ),
    "environmental_studies": (
        "environment",
        "conservation",
        "sustainability",
        "pollution",
        "biodiversity",
        "human impact",
        "climate change",
        "evs",
    ),
}

PREREQ_EDGES: tuple[tuple[str, str], ...] = (
    ("history", "civics"),
    ("geography", "environmental_studies"),
    ("civics", "political_science"),
    ("economics", "civics"),
    ("sociology", "civics"),
    ("geography", "economics"),
    ("history", "sociology"),
    ("environmental_studies", "geography"),
)


def detect_domains(text: str) -> list[dict[str, Any]]:
    return _detect_domains(text, DOMAIN_MARKERS)


def prerequisite_hints(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _prerequisite_hints(
        domains,
        PREREQ_EDGES,
        provenance="social_science_intelligence.domain_prereqs",
    )


def concept_graph_from_uli(uli: Any, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _concept_graph(
        uli,
        domains,
        PREREQ_EDGES,
        domain_node_type="social_science_domain",
        provenance="social_science_intelligence",
    )
