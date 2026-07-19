"""Progression pipeline — apply event → XP → level → badges → achievements."""

from __future__ import annotations

from typing import Any

from engines.learning_motivation_engine.achievements import evaluate_achievements
from engines.learning_motivation_engine.badges import evaluate_badges
from engines.learning_motivation_engine.levels import update_level
from engines.learning_motivation_engine.streaks import record_activity
from engines.learning_motivation_engine.xp import award_xp


def apply_progress_event(
    state: dict[str, Any],
    event: str,
    *,
    evidence_key: str,
    signals: dict[str, Any] | None = None,
    **xp_kwargs: Any,
) -> dict[str, Any]:
    signals = signals or {}
    xp_result = award_xp(state, event, evidence_key=evidence_key, **xp_kwargs)
    if not xp_result.get("ok"):
        return xp_result
    state = xp_result["state"]
    if event in ("lesson_completed", "consistent_study", "reading_completed", "tutor_session", "revision"):
        streak = record_activity(state)
        state = streak.get("state") or state
    state = update_level(state)
    badge_res = evaluate_badges(state, signals)
    state = badge_res["state"]
    ach_res = evaluate_achievements(state, signals)
    state = ach_res["state"]
    return {
        "ok": True,
        "xp_awarded": xp_result.get("xp_awarded"),
        "xp_total": state.get("xp_total"),
        "level_id": state.get("level_id"),
        "newly_earned_badges": badge_res.get("newly_earned") or [],
        "newly_unlocked_achievements": ach_res.get("newly_unlocked") or [],
        "state": state,
    }
