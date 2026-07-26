"""Speaking intelligence metadata — VMLE delivers oral practice."""

from __future__ import annotations

from typing import Any


def speaking_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    active = any(d["domain"] in {"speaking", "pronunciation"} for d in domains) or any(
        tok in (text or "").lower() for tok in ("speak", "oral", "presentation", "conversation")
    )
    return {
        "applicable": active,
        "foci": [
            "fluency",
            "expression",
            "conversation",
            "presentation_skills",
            "oral_communication",
        ],
        "practice_prompts": [
            "Plan a 30-second spoken summary of the main idea.",
            "Practise one exchange using lesson vocabulary.",
        ],
        "owner": "VMLE/ATIE",
        "provenance": "english_language_intelligence.speaking",
    }
