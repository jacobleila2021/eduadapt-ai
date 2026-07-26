"""Translation metadata — never replaces professional translation engines."""

from __future__ import annotations

from typing import Any

from engines.world_languages_intelligence._focus import build_focus_metadata

TRANSLATION_FOCI: tuple[dict[str, str], ...] = (
    {"id": "literal_meaning", "label": "Literal meaning"},
    {"id": "contextual_meaning", "label": "Contextual meaning"},
    {"id": "register", "label": "Register"},
    {"id": "formal_informal", "label": "Formal/informal usage"},
    {"id": "cultural_notes", "label": "Cultural notes"},
)


def translation_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=TRANSLATION_FOCI,
        text=text,
        domains=domains,
        domain_keys={"translation", "vocabulary", "culture"},
        provenance="world_languages_intelligence.translation",
        extra={
            "translation_drawer": True,
            "replaces_translation_engines": False,
            "invents_translations": False,
        },
    )
