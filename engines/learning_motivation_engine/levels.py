"""Meaningful levels — growth thresholds, not time-spent grinding."""

from __future__ import annotations

from typing import Any

from engines.learning_motivation_engine.schemas import LEVELS


def level_for_xp(xp: int) -> dict[str, Any]:
    current = LEVELS[0]
    nxt = None
    for i, lvl in enumerate(LEVELS):
        if xp >= int(lvl["min_xp"]):
            current = lvl
            nxt = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    progress = 1.0
    if nxt:
        span = int(nxt["min_xp"]) - int(current["min_xp"])
        progress = 0.0 if span <= 0 else min(1.0, (xp - int(current["min_xp"])) / span)
    return {
        "level": current,
        "next": nxt,
        "xp": xp,
        "progress_to_next": round(progress, 3),
        "policy": "levels_reflect_learning_growth_not_time_only",
    }


def update_level(state: dict[str, Any]) -> dict[str, Any]:
    info = level_for_xp(int(state.get("xp_total") or 0))
    state["level_id"] = info["level"]["id"]
    state["level"] = info
    return state
