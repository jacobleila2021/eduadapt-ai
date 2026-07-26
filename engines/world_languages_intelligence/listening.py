"""Listening intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.world_languages_intelligence._focus import build_focus_metadata

LISTENING_FOCI: tuple[dict[str, str], ...] = (
    {"id": "listening_comprehension", "label": "Listening comprehension"},
    {"id": "adjustable_pacing", "label": "Adjustable pacing"},
    {"id": "audio_narration", "label": "Audio narration"},
    {"id": "dictation_practice", "label": "Dictation practice"},
)


def listening_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=LISTENING_FOCI,
        text=text,
        domains=domains,
        domain_keys={"listening"},
        provenance="world_languages_intelligence.listening",
        default_count=4,
        extra={
            "owner_engine": "VMLE",
            "invents_audio": False,
        },
    )
