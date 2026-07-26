"""History intelligence metadata — source-bound; LXP renders timelines."""

from __future__ import annotations

from typing import Any

HISTORY_FOCI: tuple[dict[str, str], ...] = (
    {"id": "historical_periods", "label": "Historical periods"},
    {"id": "timelines", "label": "Timelines"},
    {"id": "chronology", "label": "Chronology"},
    {"id": "cause_and_effect", "label": "Cause and effect"},
    {"id": "historical_significance", "label": "Historical significance"},
    {"id": "primary_secondary_sources", "label": "Primary and secondary sources"},
    {"id": "interpretations", "label": "Historical interpretations"},
    {"id": "empires_civilizations", "label": "Empires and civilizations"},
    {"id": "biographies", "label": "Biographies"},
    {"id": "historical_evidence", "label": "Historical evidence"},
    {"id": "continuity_change", "label": "Continuity and change"},
)


def history_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    blob = (text or "").lower()
    active = [
        f
        for f in HISTORY_FOCI
        if f["id"].replace("_", " ") in blob or f["label"].lower() in blob
    ]
    if not active and any(d["domain"] == "history" for d in domains):
        active = [dict(f) for f in HISTORY_FOCI[:6]]
    return {
        "foci": active,
        "reasoning_prompts": [
            "What changed, and what stayed the same?",
            "Which causes were short-term vs long-term?",
            "What evidence supports this interpretation?",
        ],
        "interactive_timeline": True,
        "renderer": "lxp",
        "provenance": "social_science_intelligence.history",
    }
