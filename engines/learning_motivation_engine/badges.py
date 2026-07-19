"""Badge catalog — meaningful recognition, not addictive spam."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

BADGE_CATALOG = {
    "first_lesson": {"name": "First Steps", "category": "learning", "rarity": "common", "criteria": "Complete 1 lesson"},
    "streak_3": {"name": "Steady Spark", "category": "persistence", "rarity": "common", "criteria": "3-day healthy streak"},
    "mastery_1": {"name": "Concept Cleared", "category": "learning", "rarity": "uncommon", "criteria": "Master 1 concept"},
    "reflection_5": {"name": "Thoughtful Learner", "category": "reflection", "rarity": "uncommon", "criteria": "5 reflections"},
    "a11y_champion": {"name": "Access Ally", "category": "accessibility", "rarity": "rare", "criteria": "Use accessibility supports intentionally"},
    "math_path": {"name": "Number Navigator", "category": "mathematics", "rarity": "uncommon", "criteria": "Math mastery milestone"},
    "science_path": {"name": "Curious Catalyst", "category": "science", "rarity": "uncommon", "criteria": "Science mastery milestone"},
    "ef_planner": {"name": "Plan Pioneer", "category": "executive_function", "rarity": "rare", "criteria": "Complete EF quests"},
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def evaluate_badges(state: dict[str, Any], signals: dict[str, Any] | None = None) -> dict[str, Any]:
    signals = signals or {}
    earned_ids = {b.get("id") for b in (state.get("badges") or [])}
    new = []
    checks = [
        ("first_lesson", int(signals.get("lessons_completed") or 0) >= 1),
        ("streak_3", int((state.get("streaks") or {}).get("daily") or 0) >= 3),
        ("mastery_1", int(signals.get("concepts_mastered") or 0) >= 1),
        ("reflection_5", int(signals.get("reflections") or 0) >= 5),
        ("a11y_champion", bool(signals.get("accessibility_used"))),
        ("math_path", "mathematics" in (signals.get("subjects_mastered") or [])),
        ("science_path", "science" in (signals.get("subjects_mastered") or [])),
        ("ef_planner", int(signals.get("ef_quests_done") or 0) >= 2),
    ]
    badges = list(state.get("badges") or [])
    for bid, ok in checks:
        if ok and bid not in earned_ids and bid in BADGE_CATALOG:
            row = {"id": bid, "icon": bid, "earned_at": _now(), "educational_value": BADGE_CATALOG[bid]["criteria"], **BADGE_CATALOG[bid]}
            badges.append(row)
            new.append(row)
    state["badges"] = badges
    return {"state": state, "newly_earned": new}
