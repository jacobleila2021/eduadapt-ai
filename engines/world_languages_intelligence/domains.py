"""World languages skill-domain detection."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.taxonomy import (
    concept_graph_from_uli as _concept_graph,
    detect_domains as _detect_domains,
    prerequisite_hints as _prerequisite_hints,
)

DOMAIN_MARKERS: dict[str, tuple[str, ...]] = {
    "phonetics": (
        "phonetics",
        "phonology",
        "phoneme",
        "ipa",
        "alphabet",
        "script",
        "phonics",
    ),
    "pronunciation": (
        "pronunciation",
        "stress",
        "syllable",
        "intonation",
        "minimal pair",
        "connected speech",
        "accent",
    ),
    "grammar": (
        "grammar",
        "syntax",
        "morphology",
        "conjugation",
        "tense",
        "agreement",
        "article",
        "case",
        "word order",
        "parts of speech",
    ),
    "vocabulary": (
        "vocabulary",
        "synonym",
        "antonym",
        "cognate",
        "word family",
        "root word",
        "prefix",
        "suffix",
        "idiom",
        "expression",
    ),
    "reading": (
        "reading",
        "fluency",
        "comprehension",
        "context clue",
        "paragraph",
        "sentence parsing",
    ),
    "writing": (
        "writing",
        "essay",
        "paragraph writing",
        "cohesion",
        "academic writing",
        "sentence formation",
    ),
    "speaking": (
        "speaking",
        "conversation",
        "dialogue",
        "oral fluency",
        "speech pacing",
    ),
    "listening": (
        "listening",
        "listening comprehension",
        "audio",
        "dictation",
    ),
    "culture": (
        "culture",
        "cultural",
        "regional variation",
        "idiomatic",
        "historical context",
        "norms",
    ),
    "translation": (
        "translation",
        "literal meaning",
        "contextual meaning",
        "register",
        "formal",
        "informal",
    ),
    "literature": (
        "literature",
        "genre",
        "literary device",
        "character",
        "theme",
        "plot",
        "symbolism",
        "poetry",
        "drama",
    ),
}

PREREQ_EDGES: tuple[tuple[str, str], ...] = (
    ("phonetics", "pronunciation"),
    ("pronunciation", "speaking"),
    ("pronunciation", "listening"),
    ("vocabulary", "reading"),
    ("vocabulary", "writing"),
    ("grammar", "writing"),
    ("grammar", "speaking"),
    ("reading", "literature"),
    ("listening", "speaking"),
    ("culture", "translation"),
    ("vocabulary", "translation"),
    ("grammar", "translation"),
)


def detect_domains(text: str) -> list[dict[str, Any]]:
    return _detect_domains(text, DOMAIN_MARKERS)


def prerequisite_hints(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _prerequisite_hints(
        domains,
        PREREQ_EDGES,
        provenance="world_languages_intelligence.domain_prereqs",
    )


def concept_graph_from_uli(uli: Any, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _concept_graph(
        uli,
        domains,
        PREREQ_EDGES,
        domain_node_type="world_languages_domain",
        provenance="world_languages_intelligence",
    )
