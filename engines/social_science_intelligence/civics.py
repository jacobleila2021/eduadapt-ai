"""Civics intelligence metadata."""

from __future__ import annotations

from typing import Any

CIVICS_FOCI: tuple[dict[str, str], ...] = (
    {"id": "constitution", "label": "Constitution"},
    {"id": "democracy", "label": "Democracy"},
    {"id": "government_structures", "label": "Government structures"},
    {"id": "rights_responsibilities", "label": "Rights and responsibilities"},
    {"id": "elections", "label": "Elections"},
    {"id": "public_institutions", "label": "Public institutions"},
    {"id": "citizenship", "label": "Citizenship"},
    {"id": "rule_of_law", "label": "Rule of law"},
    {"id": "public_policy", "label": "Public policy"},
    {"id": "governance", "label": "Governance"},
)


def civics_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    blob = (text or "").lower()
    active = [
        f
        for f in CIVICS_FOCI
        if f["id"].replace("_", " ") in blob or f["label"].lower() in blob
    ]
    if not active and any(d["domain"] in {"civics", "political_science"} for d in domains):
        active = [dict(f) for f in CIVICS_FOCI[:6]]
    return {
        "foci": active,
        "civic_reasoning_prompts": [
            "Which right or duty applies in this situation?",
            "How do institutions check and balance power?",
        ],
        "comparative_government": True,
        "provenance": "social_science_intelligence.civics",
    }
