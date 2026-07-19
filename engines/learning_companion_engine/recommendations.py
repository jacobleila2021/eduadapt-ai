"""Companion recommendations — motivational next steps only."""

from __future__ import annotations

from typing import Any

from engines.learning_companion_engine.engagement import engagement_state
from engines.learning_companion_engine.emotions import infer_affect


def recommend(context: dict[str, Any] | None = None, memory: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    eng = engagement_state(context, memory)
    affect = infer_affect(context)
    recs = [
        {
            "action": "daily_check_in",
            "priority": 10 if eng.get("daily_check_in") else 40,
            "reason": "Maintain companion relationship",
            "engine": "learning_companion",
        }
    ]
    if affect["affect"] == "needs_support":
        recs.append({
            "action": "wellbeing_support",
            "priority": 5,
            "reason": "Low confidence / frustration signal",
            "engine": "learning_companion",
            "then": "handoff_atie",
        })
        recs.append({
            "action": "ask_ai_tutor",
            "priority": 6,
            "reason": "Academic help via ATIE",
            "engine": "ai_tutor",
        })
    if eng.get("disengagement_risk", 0) >= 0.55:
        recs.append({
            "action": "ef_planning",
            "priority": 8,
            "reason": "Executive function coaching for re-engagement",
            "engine": "learning_companion",
        })
    recs.append({
        "action": "celebrate_if_milestone",
        "priority": 20,
        "reason": "Sync with gamification achievements",
        "engine": "gamification",
    })
    return sorted(recs, key=lambda r: r["priority"])
