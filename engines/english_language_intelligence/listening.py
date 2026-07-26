"""Listening intelligence metadata — VMLE owns audio delivery."""

from __future__ import annotations

from typing import Any


def listening_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    active = any(d["domain"] == "listening" for d in domains) or any(
        tok in (text or "").lower() for tok in ("listen", "audio", "dictation", "recording")
    )
    return {
        "applicable": active,
        "foci": ["listening_comprehension", "note_taking", "gist_vs_detail"],
        "prompts": [
            "What is the speaker's main point?",
            "Which detail supports that point?",
        ],
        "owner": "VMLE",
        "provenance": "english_language_intelligence.listening",
    }
