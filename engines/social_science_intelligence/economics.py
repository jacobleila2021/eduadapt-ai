"""School-level economics intelligence metadata — AME owns assessment items."""

from __future__ import annotations

from typing import Any

ECONOMICS_FOCI: tuple[dict[str, str], ...] = (
    {"id": "basic_concepts", "label": "Basic economic concepts"},
    {"id": "supply_demand", "label": "Supply and demand"},
    {"id": "markets", "label": "Markets"},
    {"id": "banking", "label": "Banking"},
    {"id": "trade", "label": "Trade"},
    {"id": "budgeting", "label": "Budgeting"},
    {"id": "inflation", "label": "Inflation"},
    {"id": "employment", "label": "Employment"},
    {"id": "economic_systems", "label": "Economic systems"},
    {"id": "financial_literacy", "label": "Financial literacy"},
)


def economics_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    blob = (text or "").lower()
    active = [
        f
        for f in ECONOMICS_FOCI
        if f["id"].replace("_", " ") in blob or f["label"].lower() in blob
    ]
    if not active and any(d["domain"] == "economics" for d in domains):
        active = [dict(f) for f in ECONOMICS_FOCI[:5]]
    return {
        "foci": active,
        "reasoning_prompts": [
            "What happens to price if demand rises and supply is fixed?",
            "Who are the stakeholders in this market decision?",
        ],
        "assessment_owner": "AME",
        "provenance": "social_science_intelligence.economics",
    }
