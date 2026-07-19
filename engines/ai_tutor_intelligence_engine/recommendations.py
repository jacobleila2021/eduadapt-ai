"""Tutor recommendations for student / teacher / parent."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import TutorContext


def tutor_recommendations(ctx: TutorContext, *, mode: str, grounding_ok: bool) -> dict[str, Any]:
    student = [
        {"action": "continue_session", "detail": f"Continue in {mode} mode"},
        {"action": "request_hint", "detail": "Ask for Hint 1 before a full solution"},
    ]
    if not grounding_ok:
        student = [{"action": "review_lesson", "detail": "Return to the verified lesson materials"}]

    teacher = [
        {
            "action": "review_transcript",
            "detail": "Review tutor conversation for accuracy and support quality",
        },
        {
            "action": "set_mode",
            "detail": "Override mode / require Socratic / limit direct answers",
        },
    ]
    parent = [
        {
            "action": "home_prompt",
            "detail": "Ask your child to explain one idea from today's topic in their own words",
        },
        {
            "action": "privacy",
            "detail": "Summaries only — assessment keys are not shown to parents",
        },
    ]
    return {"student": student, "teacher": teacher, "parent": parent}
