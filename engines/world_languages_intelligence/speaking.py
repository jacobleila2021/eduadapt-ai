"""Speaking intelligence metadata — conversation scaffolds via VMLE."""

from __future__ import annotations

from typing import Any

from engines.world_languages_intelligence._focus import build_focus_metadata

SPEAKING_FOCI: tuple[dict[str, str], ...] = (
    {"id": "conversation_practice", "label": "Conversation practice"},
    {"id": "dialogue", "label": "Dialogue"},
    {"id": "pronunciation_feedback", "label": "Pronunciation feedback"},
    {"id": "speech_pacing", "label": "Speech pacing"},
    {"id": "oral_fluency", "label": "Oral fluency"},
)


def speaking_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=SPEAKING_FOCI,
        text=text,
        domains=domains,
        domain_keys={"speaking", "pronunciation"},
        provenance="world_languages_intelligence.speaking",
        extra={
            "speaking_recorder": True,
            "owner_engine": "VMLE",
            "invents_dialogues": False,
        },
    )
