"""REST-shaped API facade for Assessment & Mastery Engine."""

from __future__ import annotations

from typing import Any

from engines.assessment_mastery_engine.adaptive import adaptive_assessment
from engines.assessment_mastery_engine.assessments import generate_assessment
from engines.assessment_mastery_engine.dashboards import (
    parent_dashboard,
    school_dashboard,
    student_dashboard,
    teacher_dashboard,
)
from engines.assessment_mastery_engine.evidence import submit_answer
from engines.assessment_mastery_engine.exam_readiness import exam_readiness
from engines.assessment_mastery_engine.indexing import rebuild_ame_index
from engines.assessment_mastery_engine.intelligence import analyze_assessment_context
from engines.assessment_mastery_engine.interventions import interventions_for_weak_concepts
from engines.assessment_mastery_engine.mastery import mastery_summary, recompute_all_mastery
from engines.assessment_mastery_engine.misconceptions import detect_from_text, list_misconceptions
from engines.assessment_mastery_engine.revision import generate_revision_plan
from engines.assessment_mastery_engine.store import load_learner


def api_generate_assessment(**kwargs: Any) -> dict[str, Any]:
    if kwargs.pop("adaptive", False):
        return adaptive_assessment(**kwargs)
    return generate_assessment(**kwargs)


def api_retrieve_assessment(assessment: dict[str, Any]) -> dict[str, Any]:
    """Passthrough retrieve for generated packages (stateless)."""
    return {"ok": True, "assessment": assessment}


def api_submit_answers(learner_id: str, assessment_id: str, answers: list[dict[str, Any]]) -> dict[str, Any]:
    results = []
    for a in answers:
        results.append(
            submit_answer(
                learner_id=learner_id,
                assessment_id=assessment_id,
                item_id=str(a.get("item_id") or ""),
                response=str(a.get("response") or ""),
                official_answer=str(a.get("official_answer") or ""),
                question_type=str(a.get("question_type") or "mcq"),
                concept_id=str(a.get("concept_id") or ""),
                bloom=str(a.get("bloom") or ""),
                question=str(a.get("question") or ""),
                confidence=a.get("confidence"),
                time_sec=a.get("time_sec"),
                source=str(a.get("source") or "assessment"),
            )
        )
    return {
        "learner_id": learner_id,
        "assessment_id": assessment_id,
        "results": results,
        "mastery": recompute_all_mastery(learner_id),
    }


def api_evaluate_response(**kwargs: Any) -> dict[str, Any]:
    from engines.assessment_mastery_engine.evidence import evaluate_response

    return evaluate_response(**kwargs)


def api_retrieve_mastery(learner_id: str) -> dict[str, Any]:
    return mastery_summary(learner_id)


def api_retrieve_competencies(learner_id: str) -> dict[str, Any]:
    state = load_learner(learner_id)
    return {"learner_id": learner_id, "competencies": state.get("competencies") or {}}


def api_retrieve_interventions(concept_ids: list[str], accessibility_profiles: list[str] | None = None) -> dict[str, Any]:
    return {
        "interventions": interventions_for_weak_concepts(
            concept_ids, accessibility_profiles=accessibility_profiles
        )
    }


def api_generate_revision_plan(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    return generate_revision_plan(learner_id, **kwargs)


def api_retrieve_exam_readiness(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    return exam_readiness(learner_id, **kwargs)


def api_retrieve_analytics(learner_id: str | None = None, learner_ids: list[str] | None = None) -> dict[str, Any]:
    if learner_id:
        return {"student": student_dashboard(learner_id), "parent": parent_dashboard(learner_id)}
    return {
        "teacher": teacher_dashboard(learner_ids),
        "school": school_dashboard(learner_ids),
    }


def api_detect_misconceptions(text: str, concept_ids: list[str] | None = None) -> dict[str, Any]:
    hits = detect_from_text(text, concept_ids=concept_ids)
    return {"misconceptions": [h.to_dict() for h in hits], "catalog_size": len(list_misconceptions())}


def api_analyze_context(context: dict[str, Any]) -> dict[str, Any]:
    return analyze_assessment_context(context)


def api_rebuild_index() -> dict[str, Any]:
    return rebuild_ame_index()


def api_dashboards(role: str, learner_id: str = "", learner_ids: list[str] | None = None) -> dict[str, Any]:
    role = (role or "").lower()
    if role == "student":
        return student_dashboard(learner_id)
    if role == "parent":
        return parent_dashboard(learner_id)
    if role == "teacher":
        return teacher_dashboard(learner_ids)
    if role == "school":
        return school_dashboard(learner_ids)
    return {"error": f"unknown role: {role}"}
