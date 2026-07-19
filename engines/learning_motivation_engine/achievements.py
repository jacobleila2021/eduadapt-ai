"""Achievements — categorized, criteria-based, educational value required."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from engines.learning_motivation_engine.schemas import ACHIEVEMENT_CATEGORIES

ACHIEVEMENT_CATALOG = [
    {
        "id": "ach_persist_through_hard",
        "category": "persistence",
        "name": "Kept Going",
        "description": "Persisted through challenging practice without quitting.",
        "criteria": {"persistence_events": 3},
        "icon": "persist",
        "rarity": "uncommon",
        "educational_value": "Reinforces growth mindset and effort.",
    },
    {
        "id": "ach_reading_complete",
        "category": "reading",
        "name": "Page Turner",
        "description": "Completed a full reading passage with comprehension check.",
        "criteria": {"reading_completed": 1},
        "icon": "book",
        "rarity": "common",
        "educational_value": "Supports literacy stamina.",
    },
    {
        "id": "ach_critical_think",
        "category": "critical_thinking",
        "name": "Evidence Seeker",
        "description": "Used evidence to revise a misconception.",
        "criteria": {"misconceptions_cleared": 1},
        "icon": "think",
        "rarity": "rare",
        "educational_value": "Values reasoning over speed.",
    },
    {
        "id": "ach_collab_help",
        "category": "collaboration",
        "name": "Peer Supporter",
        "description": "Helped a classmate (teacher-approved).",
        "criteria": {"helping_classmate": 1},
        "icon": "collab",
        "rarity": "rare",
        "educational_value": "Encourages prosocial learning.",
    },
    {
        "id": "ach_creativity",
        "category": "creativity",
        "name": "Maker Mind",
        "description": "Completed a project quest.",
        "criteria": {"projects": 1},
        "icon": "create",
        "rarity": "uncommon",
        "educational_value": "Celebrates applied learning.",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def list_achievements() -> list[dict[str, Any]]:
    return list(ACHIEVEMENT_CATALOG)


def evaluate_achievements(state: dict[str, Any], signals: dict[str, Any] | None = None) -> dict[str, Any]:
    signals = signals or {}
    have = {a.get("id") for a in (state.get("achievements") or [])}
    unlocked = []
    achievements = list(state.get("achievements") or [])
    for ach in ACHIEVEMENT_CATALOG:
        if ach["id"] in have:
            continue
        crit = ach["criteria"]
        ok = all(int(signals.get(k) or 0) >= int(v) for k, v in crit.items())
        if ok:
            row = {**ach, "earned_at": _now(), "categories_available": list(ACHIEVEMENT_CATEGORIES)}
            achievements.append(row)
            unlocked.append(row)
    state["achievements"] = achievements
    return {"state": state, "newly_unlocked": unlocked}
