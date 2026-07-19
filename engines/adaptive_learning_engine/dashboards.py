"""Dashboard payloads for student / teacher / parent."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.intelligence import analyze_adaptive_context
from engines.adaptive_learning_engine.learner_model import list_learner_ids, load_learner_model


def student_dashboard(learner_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    ctx = {"learner_id": learner_id, **(context or {})}
    pkg = analyze_adaptive_context(ctx)
    return {
        "role": "student",
        "next_recommended_lesson": pkg.get("next_activity"),
        "todays_goals": (pkg.get("day_plan") or {}).get("goals") or [],
        "review_reminders": pkg.get("spaced_repetition") or [],
        "learning_path": pkg.get("learning_path"),
        "mastery_map": {
            "mastered": (pkg.get("learner_model") or {}).get("concepts_mastered"),
            "developing": (pkg.get("learner_model") or {}).get("concepts_developing"),
            "at_risk": (pkg.get("learner_model") or {}).get("concepts_at_risk"),
        },
        "confidence_indicator": pkg.get("confidence"),
        "explainability": pkg.get("explainability"),
    }


def teacher_dashboard(learner_ids: list[str] | None = None) -> dict[str, Any]:
    ids = learner_ids or list_learner_ids()
    at_risk = []
    interventions = []
    groupings = {"reteach": [], "extension": [], "on_track": []}
    for lid in ids:
        model = load_learner_model(lid)
        pkg = analyze_adaptive_context({"learner_id": lid})
        if model.concepts_at_risk or (pkg.get("predictions") or {}).get("risk_of_failure", 0) >= 0.5:
            at_risk.append({"learner_id": lid, "concepts": model.concepts_at_risk, "risk": pkg.get("predictions")})
            groupings["reteach"].append(lid)
        elif (pkg.get("enrichment") or []):
            groupings["extension"].append(lid)
        else:
            groupings["on_track"].append(lid)
        for iv in (pkg.get("interventions") or [])[:2]:
            interventions.append({"learner_id": lid, **iv})
    return {
        "role": "teacher",
        "at_risk_learners": at_risk,
        "intervention_recommendations": interventions[:20],
        "suggested_groupings": groupings,
        "learning_pathway_progress": [
            {"learner_id": lid, "model": load_learner_model(lid).to_dict()} for lid in ids
        ],
    }


def parent_dashboard(learner_id: str) -> dict[str, Any]:
    pkg = analyze_adaptive_context({"learner_id": learner_id})
    return {
        "role": "parent",
        "home_support_suggestions": (pkg.get("recommendations") or {}).get("parent") or [],
        "progress_updates": {
            "confidence": pkg.get("confidence"),
            "mastery": {
                "mastered": (pkg.get("learner_model") or {}).get("concepts_mastered"),
                "at_risk": (pkg.get("learner_model") or {}).get("concepts_at_risk"),
            },
        },
        "upcoming_reviews": pkg.get("spaced_repetition") or [],
        "recommended_activities": (pkg.get("recommendations") or {}).get("student") or [],
        "explainability": (pkg.get("explainability") or {}).get("next_activity_explanation"),
    }
