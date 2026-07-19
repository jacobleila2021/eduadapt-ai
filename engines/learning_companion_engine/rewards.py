"""Reward messaging bridge — celebrate gamification XP/badges without owning economy."""

from __future__ import annotations

from typing import Any

from engines.learning_companion_engine.celebration import celebrate


def sync_gamification_rewards(
    *,
    learner_id: str,
    gamification_payload: dict[str, Any],
    companion_id: str,
    style: str,
) -> dict[str, Any]:
    badges = gamification_payload.get("badges") or []
    streaks = gamification_payload.get("streaks") or {}
    events = []
    if badges:
        events.append(
            celebrate(
                learner_id=learner_id,
                trigger="skill_milestone",
                companion_id=companion_id,
                style=style,
                evidence={"detail": f"Badge progress: {len(badges)} badge(s).", "badges": badges[:5]},
                gamification=gamification_payload,
            )
        )
    if int(streaks.get("days") or 0) >= 1:
        events.append(
            celebrate(
                learner_id=learner_id,
                trigger="daily_consistency",
                companion_id=companion_id,
                style=style,
                evidence={"detail": f"{streaks.get('days')} day streak."},
                gamification=gamification_payload,
            )
        )
    return {"ok": True, "events": events, "xp": gamification_payload.get("xp"), "owner": "gamification_engine"}
