"""REST-shaped API facade for Adaptive Learning Engine."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.analytics import analytics_summary, record_event
from engines.adaptive_learning_engine.dashboards import parent_dashboard, student_dashboard, teacher_dashboard
from engines.adaptive_learning_engine.enrichment import generate_enrichment
from engines.adaptive_learning_engine.indexing import rebuild_ale_index
from engines.adaptive_learning_engine.intelligence import analyze_adaptive_context
from engines.adaptive_learning_engine.intervention import generate_interventions
from engines.adaptive_learning_engine.learner_model import (
    apply_teacher_override,
    load_learner_model,
    refresh_from_engines,
    save_learner_model,
)
from engines.adaptive_learning_engine.learning_path import build_learning_path
from engines.adaptive_learning_engine.predictive import predict_outcomes
from engines.adaptive_learning_engine.scheduler import next_best_activity
from engines.adaptive_learning_engine.schemas import LearnerModel
from engines.adaptive_learning_engine.spaced_repetition import schedule_reviews


def api_get_learner_model(learner_id: str) -> dict[str, Any]:
    return {"ok": True, "model": load_learner_model(learner_id).to_dict()}


def api_update_learner_state(learner_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    model = load_learner_model(learner_id)
    for k, v in updates.items():
        if hasattr(model, k) and k != "learner_id":
            setattr(model, k, v)
    save_learner_model(model)
    return {"ok": True, "model": model.to_dict()}


def api_generate_learning_pathway(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    ctx = {"learner_id": learner_id, **kwargs}
    return analyze_adaptive_context(ctx).get("learning_path") or {}


def api_get_next_activity(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    pkg = analyze_adaptive_context({"learner_id": learner_id, **kwargs})
    return pkg.get("next_activity") or {}


def api_generate_intervention_plan(learner_id: str) -> dict[str, Any]:
    model = load_learner_model(learner_id)
    rows, dec = generate_interventions(model)
    return {"interventions": rows, "explainability": dec.to_dict()}


def api_generate_enrichment_plan(learner_id: str) -> dict[str, Any]:
    model = load_learner_model(learner_id)
    rows, dec = generate_enrichment(model)
    return {"enrichment": rows, "explainability": dec.to_dict()}


def api_schedule_review(learner_id: str, concept_ids: list[str] | None = None) -> dict[str, Any]:
    model = load_learner_model(learner_id)
    rows, dec = schedule_reviews(model, concept_ids=concept_ids)
    return {"schedule": rows, "explainability": dec.to_dict()}


def api_predict_learner_outcomes(learner_id: str) -> dict[str, Any]:
    return predict_outcomes(load_learner_model(learner_id))


def api_retrieve_adaptive_analytics(learner_id: str) -> dict[str, Any]:
    return analytics_summary(learner_id, load_learner_model(learner_id).to_dict())


def api_teacher_override(
    learner_id: str,
    *,
    decision_type: str,
    choice: str,
    reason: str,
    teacher_id: str = "teacher",
) -> dict[str, Any]:
    model = apply_teacher_override(
        learner_id,
        decision_type=decision_type,
        choice=choice,
        reason=reason,
        teacher_id=teacher_id,
    )
    return {"ok": True, "model": model.to_dict()}


def api_analyze_context(context: dict[str, Any]) -> dict[str, Any]:
    return analyze_adaptive_context(context)


def api_rebuild_index() -> dict[str, Any]:
    return rebuild_ale_index()


def api_dashboards(role: str, learner_id: str = "", learner_ids: list[str] | None = None) -> dict[str, Any]:
    role = (role or "").lower()
    if role == "student":
        return student_dashboard(learner_id)
    if role == "parent":
        return parent_dashboard(learner_id)
    if role == "teacher":
        return teacher_dashboard(learner_ids)
    return {"error": f"unknown role: {role}"}
