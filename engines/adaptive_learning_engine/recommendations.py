"""Multi-audience recommendation engine — evidence over assumptions."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.schemas import LearnerModel


def build_recommendations(
    model: LearnerModel,
    *,
    path: dict[str, Any] | None = None,
    interventions: list[dict[str, Any]] | None = None,
    enrichment: list[dict[str, Any]] | None = None,
    reviews: list[dict[str, Any]] | None = None,
    predictions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = path or {}
    next_act = path.get("next_activity")
    preds = predictions or {}

    student = []
    if next_act:
        student.append(
            {
                "priority": 1,
                "action": "next_lesson",
                "detail": f"Study {next_act.get('title') or next_act.get('concept_id')} "
                f"({next_act.get('difficulty')}, {next_act.get('presentation_mode')} presentation)",
                "evidence": next_act.get("rationale"),
            }
        )
    if reviews:
        student.append({"priority": 2, "action": "review", "detail": "Complete spaced review sessions", "count": len(reviews)})
    if interventions:
        student.append(
            {
                "priority": 1 if preds.get("recommended_intervention_timing") == "immediate" else 3,
                "action": "intervention",
                "detail": interventions[0].get("title") if interventions else "Support activity",
            }
        )

    teacher = []
    if model.concepts_at_risk:
        teacher.append(
            {
                "priority": 1,
                "action": "support_group",
                "detail": f"At-risk concepts: {', '.join(model.concepts_at_risk[:5])}",
                "suggested_grouping": "small_group_reteach",
            }
        )
    for iv in (interventions or [])[:3]:
        teacher.append({"priority": 2, "action": "assign_intervention", "detail": iv.get("title"), "id": iv.get("intervention_id")})
    if enrichment:
        teacher.append({"priority": 3, "action": "extension", "detail": "Ready for enrichment pathway"})

    parent = [
        {
            "priority": 1,
            "action": "home_support",
            "detail": "Short retrieval practice using official questions only",
        }
    ]
    if reviews:
        parent.append({"priority": 2, "action": "upcoming_reviews", "detail": f"{len(reviews)} concepts scheduled"})

    special_educator = []
    if model.accessibility_profiles:
        special_educator.append(
            {
                "priority": 1,
                "action": "verify_accommodations",
                "detail": f"Profiles: {', '.join(model.accessibility_profiles)}",
            }
        )
    for iv in interventions or []:
        if iv.get("kind") in ("executive_function_supports", "teacher_intervention"):
            special_educator.append({"priority": 1, "action": "ef_scaffold", "detail": iv.get("title")})

    tutor = {
        "mastery_level": "at_risk" if model.concepts_at_risk else "developing" if model.concepts_developing else "proficient",
        "confidence": model.confidence,
        "accessibility_profiles": model.accessibility_profiles,
        "preferred_teaching_style": (next_act or {}).get("presentation_mode") or "standard",
        "misconceptions": [i.get("title") for i in (interventions or [])[:3]],
        "recommended_pacing": (next_act or {}).get("pacing") or {},
        "questioning_strategy": "socratic_depth"
        if "gifted" in (model.accessibility_profiles or [])
        else "hint_ladder",
        "never_alter_curriculum_accuracy": True,
    }

    admin = [
        {
            "priority": 1,
            "action": "monitor_risk",
            "detail": f"failure_risk={preds.get('risk_of_failure')}, disengagement={preds.get('risk_of_disengagement')}",
        }
    ]

    return {
        "student": student,
        "teacher": teacher,
        "parent": parent,
        "special_educator": special_educator,
        "tutor": tutor,
        "administrator": admin,
        "policy": "verified_evidence_over_assumptions",
    }
