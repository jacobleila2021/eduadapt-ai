"""Revision planner — ALE + AME schedules; accessibility-aware."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics
from engines.learning_experience_platform.accessibility import apply_aie
from engines.learning_experience_platform.progress import estimate_reading_minutes


def revision_planner(
    *,
    learner_id: str,
    exam_date: str = "",
    exam_days: int | None = None,
    available_minutes_per_day: int = 45,
    topic: str = "",
    lesson_text: str = "",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    a11y = apply_aie(learner_id, context)
    prefs = a11y.get("preferences") or {}

    ame_plan: dict[str, Any] = {}
    try:
        from engines.assessment_mastery_engine.service import api_generate_revision_plan

        ame_plan = api_generate_revision_plan(
            learner_id,
            topic=topic,
            exam_days=exam_days,
            accessibility_profiles=list((a11y.get("active_profiles") or prefs.get("active_profiles") or [])),
        )
    except Exception as exc:  # noqa: BLE001
        ame_plan = {"ok": False, "error": str(exc)}

    ale_reviews: dict[str, Any] = {}
    try:
        from engines.adaptive_learning_engine.service import api_schedule_review, api_generate_learning_pathway

        ale_reviews = api_schedule_review(learner_id)
        pathway = api_generate_learning_pathway(learner_id, topic=topic)
    except Exception:  # noqa: BLE001
        ale_reviews = {}
        pathway = {}

    reading_speed = float(prefs.get("reading_wpm") or 140)
    est = estimate_reading_minutes(lesson_text) if lesson_text else 0
    pace_factor = 1.2 if prefs.get("reading_mode") == "focus" else 1.0

    days = exam_days
    if days is None and exam_date:
        try:
            from datetime import date

            target = date.fromisoformat(exam_date[:10])
            days = max(1, (target - date.today()).days)
        except Exception:  # noqa: BLE001
            days = 14
    days = int(days or 14)

    daily = []
    weak = list(ame_plan.get("weak_concepts") or ame_plan.get("priority_topics") or [])[: days]
    for i in range(min(days, 21)):
        daily.append({
            "day_offset": i,
            "minutes": int(available_minutes_per_day * pace_factor),
            "focus": weak[i % len(weak)] if weak else topic or "review",
            "activities": [
                "flashcards",
                "formula_sheet",
                "official_exam_practice" if i % 3 == 2 else "revision_summary",
            ],
        })

    analytics.track("revision", learner_id=learner_id, payload={"planner": True, "days": days})
    return {
        "ok": True,
        "learner_id": learner_id,
        "exam_date": exam_date,
        "days_until_exam": days,
        "available_minutes_per_day": available_minutes_per_day,
        "reading_speed_wpm": reading_speed,
        "estimated_lesson_minutes": est,
        "accessibility_profile": prefs,
        "ame_plan": ame_plan,
        "ale_reviews": ale_reviews,
        "pathway": pathway,
        "schedule": daily,
        "policy": {"verified_practice_only": True},
    }
