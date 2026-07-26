"""Vocabulary intelligence metadata — lesson-bound; no invented definitions."""

from __future__ import annotations

from typing import Any

from engines.world_languages_intelligence._focus import build_focus_metadata

VOCABULARY_FOCI: tuple[dict[str, str], ...] = (
    {"id": "definitions", "label": "Definitions"},
    {"id": "synonyms", "label": "Synonyms"},
    {"id": "antonyms", "label": "Antonyms"},
    {"id": "cognates", "label": "Cognates"},
    {"id": "word_families", "label": "Word families"},
    {"id": "root_words", "label": "Root words"},
    {"id": "prefixes", "label": "Prefixes"},
    {"id": "suffixes", "label": "Suffixes"},
    {"id": "frequency", "label": "Frequency"},
    {"id": "difficulty", "label": "Difficulty"},
    {"id": "idioms", "label": "Idioms"},
    {"id": "expressions", "label": "Expressions"},
)


def vocabulary_metadata(text: str, domains: list[dict[str, Any]], uli: Any = None) -> dict[str, Any]:
    lesson_terms: list[str] = []
    try:
        if uli is not None:
            learn = dict(uli.learning_structure())
            for c in learn.get("key_concepts") or []:
                if isinstance(c, dict) and c.get("concept"):
                    lesson_terms.append(str(c["concept"]))
    except Exception:  # noqa: BLE001
        pass
    return build_focus_metadata(
        foci_catalogue=VOCABULARY_FOCI,
        text=text,
        domains=domains,
        domain_keys={"vocabulary", "reading", "writing"},
        provenance="world_languages_intelligence.vocabulary",
        default_count=8,
        extra={
            "lesson_bound_terms": lesson_terms[:24],
            "vocabulary_popups": True,
            "invents_definitions": False,
        },
    )
