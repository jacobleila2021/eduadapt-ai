"""Reading intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.world_languages_intelligence._focus import build_focus_metadata

READING_FOCI: tuple[dict[str, str], ...] = (
    {"id": "reading_fluency", "label": "Reading fluency"},
    {"id": "reading_comprehension", "label": "Reading comprehension"},
    {"id": "vocabulary_growth", "label": "Vocabulary growth"},
    {"id": "context_clues", "label": "Context clues"},
    {"id": "sentence_parsing", "label": "Sentence parsing"},
    {"id": "paragraph_structure", "label": "Paragraph structure"},
)


def reading_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=READING_FOCI,
        text=text,
        domains=domains,
        domain_keys={"reading", "literature"},
        provenance="world_languages_intelligence.reading",
        extra={
            "read_aloud": True,
            "read_along": True,
            "owner_engine": "VMLE/AIE",
        },
    )
