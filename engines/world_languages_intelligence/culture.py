"""Culture and literature intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.world_languages_intelligence._focus import build_focus_metadata

CULTURE_FOCI: tuple[dict[str, str], ...] = (
    {"id": "cultural_norms", "label": "Cultural norms"},
    {"id": "regional_variations", "label": "Regional variations"},
    {"id": "idiomatic_usage", "label": "Idiomatic usage"},
    {"id": "historical_context", "label": "Historical context"},
)

LITERATURE_FOCI: tuple[dict[str, str], ...] = (
    {"id": "genre", "label": "Genre"},
    {"id": "literary_devices", "label": "Literary devices"},
    {"id": "character", "label": "Character"},
    {"id": "theme", "label": "Theme"},
    {"id": "plot", "label": "Plot"},
    {"id": "symbolism", "label": "Symbolism"},
    {"id": "poetry", "label": "Poetry"},
    {"id": "drama", "label": "Drama"},
)


def culture_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    culture = build_focus_metadata(
        foci_catalogue=CULTURE_FOCI,
        text=text,
        domains=domains,
        domain_keys={"culture", "translation"},
        provenance="world_languages_intelligence.culture",
        default_count=4,
    )
    literature = build_focus_metadata(
        foci_catalogue=LITERATURE_FOCI,
        text=text,
        domains=domains,
        domain_keys={"literature", "reading"},
        provenance="world_languages_intelligence.literature",
    )
    return {
        **culture,
        "literature": literature,
        "invents_cultural_facts": False,
    }
