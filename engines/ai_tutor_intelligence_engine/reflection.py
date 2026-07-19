"""Reflection prompts — store via session memory / learner profile hooks."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import TutorContext


def reflection_prompts(ctx: TutorContext) -> dict[str, Any]:
    return {
        "prompts": [
            "What did you learn in this session?",
            "What is still confusing?",
            f"How confident do you feel about {ctx.topic or 'this topic'} (0–100%)?",
            "Which strategy helped most (hint, diagram, worked example, questioning)?",
            "What is your next goal?",
        ],
        "store_fields": ["learned", "confusing", "confidence", "strategies", "next_goal"],
        "policy": "reflection_for_learning_profile_not_medical",
    }


def format_reflection_record(answers: dict[str, Any]) -> dict[str, Any]:
    return {
        "learned": answers.get("learned") or "",
        "confusing": answers.get("confusing") or "",
        "confidence": answers.get("confidence"),
        "strategies": answers.get("strategies") or "",
        "next_goal": answers.get("next_goal") or "",
    }
