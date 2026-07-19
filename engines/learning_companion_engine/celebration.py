"""Celebration system — hooks into Gamification Engine payloads; no invented XP."""

from __future__ import annotations

from typing import Any

from engines.learning_companion_engine.learner_memory import record_achievement
from engines.learning_companion_engine.personality import apply_style
from engines.learning_companion_engine.schemas import CompanionMessage

CELEBRATION_TRIGGERS = (
    "lesson_completed",
    "concept_mastered",
    "misconception_cleared",
    "reading_fluency_improved",
    "daily_consistency",
    "weekly_goal",
    "skill_milestone",
    "competency_achieved",
)


def celebrate(
    *,
    learner_id: str,
    trigger: str,
    companion_id: str = "study_panda",
    style: str = "cheerful_friend",
    evidence: dict[str, Any] | None = None,
    gamification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = evidence or {}
    trigger = trigger if trigger in CELEBRATION_TRIGGERS else "skill_milestone"
    labels = {
        "lesson_completed": "You finished today's lesson.",
        "concept_mastered": "You mastered a concept — that's real growth.",
        "misconception_cleared": "You cleared a misconception. Understanding just got clearer.",
        "reading_fluency_improved": "Your reading fluency is improving.",
        "daily_consistency": "You showed up again today — habits unlock skill.",
        "weekly_goal": "Weekly goal achieved.",
        "skill_milestone": "Skill milestone reached.",
        "competency_achieved": "Competency unlocked.",
    }
    base = labels[trigger]
    if evidence.get("detail"):
        base = f"{base} {evidence['detail']}"
    styled = apply_style(base, style)
    game = gamification or {}
    msg = CompanionMessage(
        text=styled["text"],
        kind="celebration",
        companion_id=companion_id,
        evidence=[{"trigger": trigger, **evidence}, {"gamification_snapshot": {
            "xp": game.get("xp"), "badges": game.get("badges"), "streaks": game.get("streaks")
        }}],
        speakable=True,
    )
    mem = record_achievement(
        learner_id,
        {"trigger": trigger, "message": msg.text, "evidence": evidence, "source": "alcis+gamification"},
    )
    return {"ok": True, "message": msg.to_dict(), "memory": mem, "integrates": "gamification_engine"}
