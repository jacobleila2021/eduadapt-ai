"""Engagement signals for companion frequency & check-ins."""

from __future__ import annotations

from typing import Any


def engagement_state(context: dict[str, Any] | None = None, memory: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    memory = memory or {}
    outputs = context.get("engine_outputs") or {}
    ale = (outputs.get("adaptive_learning") or {}).get("payload") or {}
    laie = (outputs.get("learning_analytics") or {}).get("payload") or {}
    preds = ale.get("predictions") or laie.get("predictions") or {}
    risk = float(preds.get("risk_of_disengagement") or 0)
    freq = memory.get("interaction_frequency") or "medium"
    if risk >= 0.55:
        freq = "high"
    return {
        "disengagement_risk": risk,
        "recommended_frequency": freq,
        "daily_check_in": risk >= 0.4 or freq == "high",
        "celebrate_small_wins": True,
        "source": ["adaptive_learning", "learning_analytics"],
    }
