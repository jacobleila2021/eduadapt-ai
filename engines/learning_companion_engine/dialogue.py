"""Dialogue helpers — greetings, tutor handoff, check-ins (no teaching)."""

from __future__ import annotations

from typing import Any

from engines.learning_companion_engine.avatars import get_companion
from engines.learning_companion_engine.personality import apply_style
from engines.learning_companion_engine.schemas import CompanionMessage


def greeting(*, companion_id: str, style: str, learner_name: str = "") -> dict[str, Any]:
    companion = get_companion(companion_id)
    name = learner_name or "friend"
    raw = f"Hi {name} — {companion['name']} here. Ready when you are."
    styled = apply_style(raw, style)
    msg = CompanionMessage(text=styled["text"], kind="greeting", companion_id=companion_id, speakable=True)
    return {"ok": True, "message": msg.to_dict(), "companion": companion}


def handoff_to_atie(*, companion_id: str, style: str, topic: str = "") -> dict[str, Any]:
    topic_bit = f" about {topic}" if topic else ""
    raw = (
        f"For explanations{topic_bit}, I'll bring in your AI Tutor — they handle the learning steps. "
        "I'll stay with you for encouragement."
    )
    styled = apply_style(raw, style)
    msg = CompanionMessage(
        text=styled["text"],
        kind="handoff_tutor",
        companion_id=companion_id,
        speakable=True,
        refer_to_atie=True,
    )
    return {
        "ok": True,
        "message": msg.to_dict(),
        "atie_required": True,
        "policy": "companion_never_teaches_independently",
    }


def daily_check_in(*, companion_id: str, style: str, streak_days: int = 0) -> dict[str, Any]:
    raw = f"Quick check-in: how is energy today? Streak: {streak_days} day(s). One small goal is enough."
    styled = apply_style(raw, style)
    msg = CompanionMessage(text=styled["text"], kind="greeting", companion_id=companion_id, speakable=True)
    return {"ok": True, "message": msg.to_dict()}
