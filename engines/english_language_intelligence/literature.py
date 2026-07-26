"""Literature intelligence — identify concepts present in verified lesson content only."""

from __future__ import annotations

from typing import Any

LITERATURE_LENSES: tuple[dict[str, str], ...] = (
    {"id": "poetry", "label": "Poetry"},
    {"id": "drama", "label": "Drama"},
    {"id": "fiction", "label": "Fiction"},
    {"id": "non_fiction", "label": "Non-fiction"},
    {"id": "character_analysis", "label": "Character analysis"},
    {"id": "plot", "label": "Plot"},
    {"id": "theme", "label": "Theme"},
    {"id": "symbolism", "label": "Symbolism"},
    {"id": "imagery", "label": "Imagery"},
    {"id": "literary_devices", "label": "Literary devices"},
    {"id": "mood", "label": "Mood"},
    {"id": "tone", "label": "Tone"},
    {"id": "figurative_language", "label": "Figurative language"},
    {"id": "context", "label": "Context"},
    {"id": "author_background", "label": "Author background"},
)


def literature_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    blob = (text or "").lower()
    active = []
    for lens in LITERATURE_LENSES:
        keys = (lens["id"].replace("_", " "), lens["label"].lower())
        if any(k in blob for k in keys):
            active.append(lens)
    if not active and any(d["domain"] == "literature" for d in domains):
        active = [dict(l) for l in LITERATURE_LENSES if l["id"] in {"theme", "character_analysis", "plot", "figurative_language"}]
    return {
        "lenses": active,
        "annotation_prompts": [
            "Which literary device is used, and what effect does it create?",
            "How does a character change, and what evidence shows it?",
            "State a theme as an insight (not just a topic word).",
        ],
        "source_bound": True,
        "provenance": "english_language_intelligence.literature",
    }
