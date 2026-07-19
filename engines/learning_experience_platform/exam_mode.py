"""Official exam mode — AME question banks only; companion suppressed."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics
from engines.learning_experience_platform.phase3_schemas import EXAM_MODES


def exam_mode(
    *,
    learner_id: str,
    topic: str = "",
    lesson_text: str = "",
    mode: str = "practice",
    context: dict[str, Any] | None = None,
    timed_seconds: int | None = None,
) -> dict[str, Any]:
    mode = mode if mode in EXAM_MODES else "practice"
    context = context or {}
    assessment: dict[str, Any] = {}
    readiness: dict[str, Any] = {}
    try:
        from engines.assessment_mastery_engine.service import (
            api_generate_assessment,
            api_retrieve_exam_readiness,
        )

        assessment = api_generate_assessment(
            assessment_type="summative" if mode in ("timed", "teacher") else "formative",
            topic=topic,
            lesson_text=lesson_text,
            learner_id=learner_id,
            limit=8,
        )
        readiness = api_retrieve_exam_readiness(learner_id, topic=topic)
    except Exception as exc:  # noqa: BLE001
        assessment = {"ok": False, "error": str(exc), "items": [], "fallback": True}
        readiness = {"ok": False}

    items = []
    raw_items = assessment.get("items") or []
    if isinstance(raw_items, list):
        for it in raw_items:
            if hasattr(it, "to_dict"):
                items.append(it.to_dict())
            elif isinstance(it, dict):
                items.append(it)

    bundle = assessment.get("exam_bundle") or assessment.get("bundle") or {}
    categorized = {
        "official": items,
        "previous_year": bundle.get("pyq") or bundle.get("previous_year") or [],
        "competency": bundle.get("competency") or [],
        "hots": bundle.get("hots") or [],
        "exemplar": bundle.get("exemplar") or [],
    }

    display = []
    for it in items:
        display.append({
            "item_id": it.get("item_id"),
            "question": it.get("question"),
            "bloom": it.get("bloom"),
            "marks": it.get("marks"),
            "difficulty": it.get("difficulty"),
            "source": it.get("source"),
            "official_answer": it.get("official_answer") if mode in ("review", "teacher") else None,
            "answer_revealed": mode in ("review", "teacher"),
        })

    analytics.track("exam", learner_id=learner_id, payload={"mode": mode, "item_count": len(display)})
    return {
        "ok": True,
        "mode": mode,
        "topic": topic,
        "timed_seconds": timed_seconds if mode == "timed" else None,
        "questions": display,
        "categories": {k: len(v) if isinstance(v, list) else 0 for k, v in categorized.items()},
        "bundle": categorized if mode == "teacher" else {k: (v if k == "official" else []) for k, v in categorized.items()},
        "exam_readiness": readiness,
        "companion_suppressed": True,
        "motivation_suppressed": mode in ("timed", "practice"),
        "policy": {
            "official_answers_from_verified_banks_only": True,
            "never_invent_questions": True,
            "companion_never_interrupts_assessment": True,
        },
    }


def official_exam_bundle(*, topic: str = "", learner_id: str = "") -> dict[str, Any]:
    """Thin wrapper for previous-year / exemplar bundles via AME."""
    return exam_mode(learner_id=learner_id or "anonymous", topic=topic, mode="teacher")
