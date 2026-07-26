"""Grammar intelligence metadata — cues for ATIE explanations only."""

from __future__ import annotations

from typing import Any

GRAMMAR_FOCI: tuple[dict[str, str], ...] = (
    {"id": "parts_of_speech", "label": "Parts of speech"},
    {"id": "sentence_structure", "label": "Sentence structure"},
    {"id": "tenses", "label": "Tenses"},
    {"id": "clauses", "label": "Clauses"},
    {"id": "punctuation", "label": "Punctuation"},
    {"id": "subject_verb_agreement", "label": "Subject-verb agreement"},
    {"id": "voice", "label": "Voice (active/passive)"},
    {"id": "reported_speech", "label": "Reported speech"},
    {"id": "cohesion", "label": "Cohesion"},
    {"id": "cohesive_devices", "label": "Cohesive devices"},
    {"id": "editing_cues", "label": "Editing cues"},
)


def grammar_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    blob = (text or "").lower()
    active = [g for g in GRAMMAR_FOCI if g["id"].replace("_", " ") in blob or g["label"].lower() in blob]
    if not active and any(d["domain"] == "grammar" for d in domains):
        active = [dict(g) for g in GRAMMAR_FOCI[:6]]
    return {
        "foci": active,
        "editing_cues": [
            "Check subject–verb agreement in each clause.",
            "Verify tense consistency across the paragraph.",
            "Confirm punctuation supports intended sentence boundaries.",
        ],
        "explanation_owner": "ATIE",
        "provenance": "english_language_intelligence.grammar",
    }
