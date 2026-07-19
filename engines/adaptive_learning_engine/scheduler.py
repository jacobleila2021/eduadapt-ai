"""Activity scheduler — next best activity from pathway + reviews."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

from engines.adaptive_learning_engine.schemas import LearnerModel


def next_best_activity(
    model: LearnerModel,
    *,
    path: dict[str, Any] | None = None,
    reviews: list[dict[str, Any]] | None = None,
    interventions: list[dict[str, Any]] | None = None,
    predictions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = path or {}
    reviews = reviews or []
    interventions = interventions or []
    preds = predictions or {}
    today = date.today().isoformat()

    # Due reviews today take priority when failure risk elevated
    due = []
    for block in reviews:
        for s in block.get("sessions") or []:
            if s.get("date") == today or s.get("day_offset") == 0:
                due.append({"concept_id": block.get("concept_id"), **s})

    if due and preds.get("recommended_intervention_timing") in ("immediate", "soon"):
        return {
            "activity_type": "review",
            "concept_id": due[0].get("concept_id"),
            "reason": "Spaced review due; elevated risk warrants retrieval practice",
            "source": "spaced_repetition",
        }

    if preds.get("recommended_intervention_timing") == "immediate" and interventions:
        return {
            "activity_type": "intervention",
            "intervention": interventions[0],
            "reason": interventions[0].get("reason") or interventions[0].get("title"),
            "source": "intervention_engine",
        }

    next_act = path.get("next_activity")
    if next_act:
        return {
            "activity_type": next_act.get("activity_type") or "lesson",
            "concept_id": next_act.get("concept_id"),
            "difficulty": next_act.get("difficulty"),
            "presentation_mode": next_act.get("presentation_mode"),
            "estimated_minutes": next_act.get("estimated_minutes"),
            "reason": next_act.get("rationale"),
            "explainability": (path.get("explainability") or {}),
            "source": "learning_path",
            "chapter_cache_hint": "Reuse teacher-approved chapter cache when available",
        }

    return {
        "activity_type": "explore",
        "reason": "No queued steps — continue with standard pathway from CIE recommendations",
        "source": "fallback",
    }


def schedule_day_plan(
    model: LearnerModel,
    *,
    path: dict[str, Any] | None = None,
    reviews: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    next_act = next_best_activity(model, path=path, reviews=reviews)
    goals = []
    if next_act.get("concept_id"):
        goals.append(f"Complete {next_act['activity_type']} on {next_act['concept_id']}")
    goals.append("Log confidence after practice")
    return {
        "date": datetime.now(timezone.utc).date().isoformat(),
        "learner_id": model.learner_id,
        "goals": goals,
        "next_activity": next_act,
        "review_blocks": reviews or [],
    }
