"""Grammar intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.world_languages_intelligence._focus import build_focus_metadata

GRAMMAR_FOCI: tuple[dict[str, str], ...] = (
    {"id": "parts_of_speech", "label": "Parts of speech"},
    {"id": "verb_conjugation", "label": "Verb conjugation"},
    {"id": "tenses", "label": "Tenses"},
    {"id": "agreement", "label": "Agreement"},
    {"id": "articles", "label": "Articles"},
    {"id": "cases", "label": "Cases"},
    {"id": "word_order", "label": "Word order"},
    {"id": "sentence_patterns", "label": "Sentence patterns"},
    {"id": "syntax", "label": "Syntax"},
    {"id": "morphology", "label": "Morphology"},
    {"id": "semantics", "label": "Semantics"},
)


def grammar_metadata(
    text: str,
    domains: list[dict[str, Any]],
    languages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    highlights = []
    for lang in languages or []:
        highlights.extend(lang.get("grammar_highlights") or [])
    return build_focus_metadata(
        foci_catalogue=GRAMMAR_FOCI,
        text=text,
        domains=domains,
        domain_keys={"grammar"},
        provenance="world_languages_intelligence.grammar",
        default_count=8,
        extra={
            "language_highlights": highlights[:16],
            "grammar_panels": True,
            "invents_rules": False,
        },
    )
