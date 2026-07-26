"""Pronunciation metadata — intelligibility focus; VMLE narrates."""

from __future__ import annotations

from typing import Any


def pronunciation_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    active = any(d["domain"] == "pronunciation" for d in domains) or any(
        tok in (text or "").lower() for tok in ("pronunciation", "phonics", "intonation", "stress")
    )
    return {
        "applicable": active,
        "foci": ["pronunciation", "fluency", "intonation", "word_stress", "intelligibility"],
        "guidance": [
            "Prioritise clear phonemes and word stress over accent imitation.",
            "Use click-to-pronounce for lesson vocabulary (VMLE).",
        ],
        "owner": "VMLE",
        "provenance": "english_language_intelligence.pronunciation",
    }
