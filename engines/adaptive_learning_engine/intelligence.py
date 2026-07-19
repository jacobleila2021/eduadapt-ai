"""Adaptive Learning intelligence — decision orchestration for VLIE."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.analytics import analytics_summary, record_event
from engines.adaptive_learning_engine.confidence import estimate_confidence
from engines.adaptive_learning_engine.enrichment import generate_enrichment
from engines.adaptive_learning_engine.indexing import rebuild_ale_index
from engines.adaptive_learning_engine.intervention import generate_interventions
from engines.adaptive_learning_engine.learner_model import refresh_from_engines
from engines.adaptive_learning_engine.learning_path import build_learning_path
from engines.adaptive_learning_engine.misconceptions import detect_misconceptions
from engines.adaptive_learning_engine.predictive import predict_outcomes
from engines.adaptive_learning_engine.recommendations import build_recommendations
from engines.adaptive_learning_engine.scheduler import next_best_activity, schedule_day_plan
from engines.adaptive_learning_engine.spaced_repetition import schedule_reviews


def _payload(engine_outputs: dict[str, Any], engine_id: str) -> dict[str, Any]:
    block = engine_outputs.get(engine_id) or {}
    if isinstance(block, dict):
        return block.get("payload") or {}
    return {}


def analyze_adaptive_context(context: dict[str, Any]) -> dict[str, Any]:
    """
    Full ALE decision package.
    Does not generate lessons — selects pathway/difficulty/pacing/reviews/interventions.
    """
    outputs = context.get("engine_outputs") or {}
    aie = _payload(outputs, "accessibility")
    cie = _payload(outputs, "curriculum").get("curriculum_intelligence") or {}
    # curriculum payload may nest differently
    if not cie and _payload(outputs, "curriculum"):
        cie = _payload(outputs, "curriculum").get("curriculum_intelligence") or {}
    ame = _payload(outputs, "assessment")

    learner_id = context.get("learner_id") or context.get("student_id") or "anonymous"
    model = refresh_from_engines(
        learner_id,
        context=context,
        cie=cie,
        ame=ame,
        aie=aie,
    )

    # Confidence update
    conf = estimate_confidence(model, ame=ame, self_reported=context.get("self_reported_confidence"))
    model.confidence = float(conf["confidence"])
    from engines.adaptive_learning_engine.learner_model import save_learner_model

    save_learner_model(model)

    readability = (aie.get("readability") or {})
    cognitive_load = readability.get("cognitive_load") or "medium"

    pathway_type = context.get("pathway_type") or "mastery"
    if model.concepts_at_risk:
        pathway_type = context.get("pathway_type") or "remediation"
    elif "gifted" in model.accessibility_profiles and not model.concepts_at_risk:
        pathway_type = context.get("pathway_type") or "enrichment"

    path = build_learning_path(
        model,
        cie=cie,
        aie=aie,
        pathway_type=pathway_type,
        teacher_priorities=context.get("teacher_priorities"),
        allow_skip_prerequisites=bool(context.get("allow_skip_prerequisites")),
        cognitive_load=cognitive_load,
    )

    misc = detect_misconceptions(model, lesson_text=context.get("lesson_text") or "", ame=ame)
    interventions, interv_dec = generate_interventions(model, misconceptions=misc, ame=ame)
    enrichment, enrich_dec = generate_enrichment(model, cie=cie)
    reviews, sr_dec = schedule_reviews(model)
    predictions = predict_outcomes(model, ame=ame)

    next_act = next_best_activity(
        model,
        path=path,
        reviews=reviews,
        interventions=interventions,
        predictions=predictions,
    )
    day_plan = schedule_day_plan(model, path=path, reviews=reviews)
    recs = build_recommendations(
        model,
        path=path,
        interventions=interventions,
        enrichment=enrichment,
        reviews=reviews,
        predictions=predictions,
    )

    # Backward-compatible keys for AdaptiveLearningEngine v1 consumers
    profiles = aie.get("profiles_generated") or model.accessibility_profiles or ["standard"]
    presentation = (path.get("next_activity") or {}).get("presentation_mode") or (
        profiles[0] if profiles else "standard"
    )

    # Human-readable explainability summary (Teacher Override & Explainability Layer)
    explain_summary = path.get("explainability") or {}
    if next_act.get("concept_id"):
        explain_summary = {
            **explain_summary,
            "next_activity_explanation": (
                f"This learner is being recommended the '{presentation}' presentation with "
                f"difficulty '{next_act.get('difficulty')}' on concept '{next_act.get('concept_id')}' "
                f"because confidence is {model.confidence:.0%}, "
                f"{len(model.concepts_at_risk)} concepts are at risk, "
                f"{len(misc)} misconceptions were detected, "
                f"and accessibility profiles indicate {model.accessibility_profiles or ['standard']}."
            ),
        }

    if learner_id != "anonymous":
        try:
            record_event(learner_id, "pathway_change", {"path_id": path.get("path_id"), "type": pathway_type})
        except Exception:  # noqa: BLE001
            pass

    return {
        # v1 compatibility
        "pathways": profiles if isinstance(profiles, list) else [presentation],
        "pacing": (path.get("next_activity") or {}).get("pacing") or "profile-driven",
        "scaffolding": "hint ladders for tutor; chunks for ADHD — from AIE/ALE",
        "difficulty_adaptation": "presentation only — STEM facts locked",
        "next_best_lesson": next_act,
        "difference_target": 0.80,
        # ALE enrichment
        "learner_model": model.to_dict(),
        "learning_path": path,
        "next_activity": next_act,
        "day_plan": day_plan,
        "spaced_repetition": reviews,
        "misconceptions": misc,
        "interventions": interventions,
        "enrichment": enrichment,
        "predictions": predictions,
        "confidence": conf,
        "recommendations": recs,
        "tutor_brief": recs.get("tutor") or {},
        "explainability": explain_summary,
        "decisions": (path.get("decisions") or [])
        + [interv_dec.to_dict(), enrich_dec.to_dict(), sr_dec.to_dict(), predictions.get("explainability") or {}],
        "analytics": analytics_summary(learner_id, model.to_dict()),
        "policy": {
            "does_not_generate_lessons": True,
            "consumes_cie_ame_aie": True,
            "deterministic_explainable": True,
            "teacher_override_allowed": True,
            "curriculum_facts_locked": True,
        },
        "ale_version": "2.0.0",
    }


def ensure_indexed() -> dict[str, Any]:
    return rebuild_ale_index()
