"""Pronunciation intelligence metadata — reuses VMLE; no invented audio."""

from __future__ import annotations

from typing import Any

from engines.world_languages_intelligence._focus import build_focus_metadata

PRONUNCIATION_FOCI: tuple[dict[str, str], ...] = (
    {"id": "ipa", "label": "IPA"},
    {"id": "stress", "label": "Stress"},
    {"id": "syllables", "label": "Syllables"},
    {"id": "intonation", "label": "Intonation"},
    {"id": "connected_speech", "label": "Connected speech"},
    {"id": "minimal_pairs", "label": "Minimal pairs"},
    {"id": "phoneme_practice", "label": "Phoneme practice"},
)


def pronunciation_metadata(
    text: str,
    domains: list[dict[str, Any]],
    languages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    notes = []
    for lang in languages or []:
        notes.extend(lang.get("pronunciation_notes") or [])
    return build_focus_metadata(
        foci_catalogue=PRONUNCIATION_FOCI,
        text=text,
        domains=domains,
        domain_keys={"pronunciation", "phonetics", "speaking"},
        provenance="world_languages_intelligence.pronunciation",
        default_count=7,
        extra={
            "language_notes": notes[:12],
            "click_pronunciation": True,
            "pronunciation_waveform": True,
            "owner_engine": "VMLE",
            "invents_audio": False,
        },
    )
