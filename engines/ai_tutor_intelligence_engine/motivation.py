"""Motivation micro-prompts — accessibility-first, no dark patterns."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import TutorContext


def motivation_nudge(ctx: TutorContext) -> dict[str, Any]:
    if ctx.confidence < 0.4:
        msg = "Progress over perfection — one clear idea from your materials is a win."
    elif ctx.misconceptions:
        msg = "Spotting a mix-up is part of learning. Let's correct it with verified facts."
    else:
        msg = "Nice focus. Try explaining the idea in one sentence without looking."
    return {
        "message": msg,
        "style": "encouraging",
        "dark_patterns": False,
        "ties_to_gamification": "optional_quests_only",
    }
