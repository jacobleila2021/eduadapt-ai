"""English language domain detection — literacy/language focus (curriculum-agnostic)."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.taxonomy import (
    concept_graph_from_uli as _concept_graph,
    detect_domains as _detect_domains,
    prerequisite_hints as _prerequisite_hints,
)

DOMAIN_MARKERS: dict[str, tuple[str, ...]] = {
    "reading": (
        "reading",
        "comprehension",
        "fluency",
        "close reading",
        "guided reading",
        "inference",
        "main idea",
        "summaris",
        "summariz",
        "author's purpose",
        "point of view",
    ),
    "vocabulary": (
        "vocabulary",
        "word meaning",
        "synonym",
        "antonym",
        "prefix",
        "suffix",
        "root word",
        "idiom",
        "collocation",
        "context clue",
        "academic vocabulary",
    ),
    "grammar": (
        "grammar",
        "parts of speech",
        "tense",
        "punctuation",
        "subject-verb",
        "clause",
        "reported speech",
        "active voice",
        "passive voice",
        "cohesion",
    ),
    "writing": (
        "writing",
        "essay",
        "paragraph",
        "narrative",
        "persuasive",
        "descriptive",
        "expository",
        "thesis",
        "draft",
        "revision",
        "editing",
    ),
    "literature": (
        "literature",
        "poetry",
        "poem",
        "drama",
        "fiction",
        "non-fiction",
        "character",
        "theme",
        "symbolism",
        "imagery",
        "metaphor",
        "simile",
        "figurative",
    ),
    "speaking": (
        "speaking",
        "oral",
        "presentation",
        "conversation",
        "pronunciation",
        "intonation",
        "fluency",
        "expression",
    ),
    "listening": (
        "listening",
        "listen",
        "audio",
        "comprehension audio",
        "dictation",
        "oral comprehension",
    ),
    "pronunciation": (
        "pronunciation",
        "phonics",
        "phoneme",
        "stress",
        "accent",
        "articulate",
    ),
}

PREREQ_EDGES: tuple[tuple[str, str], ...] = (
    ("vocabulary", "reading"),
    ("grammar", "writing"),
    ("reading", "literature"),
    ("vocabulary", "writing"),
    ("reading", "writing"),
    ("listening", "speaking"),
    ("pronunciation", "speaking"),
    ("grammar", "speaking"),
    ("vocabulary", "literature"),
)


def detect_domains(text: str) -> list[dict[str, Any]]:
    return _detect_domains(text, DOMAIN_MARKERS)


def prerequisite_hints(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _prerequisite_hints(
        domains,
        PREREQ_EDGES,
        provenance="english_language_intelligence.domain_prereqs",
    )


def concept_graph_from_uli(uli: Any, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _concept_graph(
        uli,
        domains,
        PREREQ_EDGES,
        domain_node_type="english_domain",
        provenance="english_language_intelligence",
    )
