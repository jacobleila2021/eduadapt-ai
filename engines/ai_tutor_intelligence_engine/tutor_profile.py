"""Load learner tutoring context from VLIE engine outputs (never invent)."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import TutorContext


def _payload(outputs: dict[str, Any], engine_id: str) -> dict[str, Any]:
    block = (outputs or {}).get(engine_id) or {}
    if not isinstance(block, dict):
        return {}
    return block.get("payload") or {}


def build_tutor_context(context: dict[str, Any]) -> TutorContext:
    outputs = context.get("engine_outputs") or {}
    cie_wrap = _payload(outputs, "curriculum")
    cie = cie_wrap.get("curriculum_intelligence") or cie_wrap
    ame = _payload(outputs, "assessment")
    aie = _payload(outputs, "accessibility")
    ale = _payload(outputs, "adaptive_learning")
    laie = _payload(outputs, "learning_analytics")

    model = ale.get("learner_model") or {}
    matched = cie.get("matched_concepts") or []
    concept_ids = [m.get("concept_id") for m in matched if isinstance(m, dict) and m.get("concept_id")]
    if cie.get("primary_concept_id") and cie["primary_concept_id"] not in concept_ids:
        concept_ids.insert(0, cie["primary_concept_id"])

    los = []
    for o in cie.get("learning_outcomes") or []:
        if isinstance(o, dict):
            los.append(o.get("statement") or o.get("outcome_id") or "")
        else:
            los.append(str(o))

    mastery = "developing"
    if model.get("concepts_at_risk"):
        mastery = "beginning"
    elif model.get("concepts_mastered") and not model.get("concepts_developing"):
        mastery = "proficient"

    conf = float(model.get("confidence") or (ale.get("confidence") or {}).get("confidence") or 0.5)
    profiles = (
        (aie.get("learner_profile") or {}).get("active_profiles")
        or aie.get("profiles_generated")
        or model.get("accessibility_profiles")
        or []
    )
    presentation = ((aie.get("presentation") or {}).get("primary_mode")) or (
        ((ale.get("next_activity") or {}).get("presentation_mode")) or "standard"
    )
    reading = ((aie.get("readability") or {}).get("reading_level")) or (
        ((laie.get("report") or {}).get("reading_level")) or ""
    )

    return TutorContext(
        learner_id=str(context.get("learner_id") or context.get("student_id") or "anonymous"),
        topic=str(context.get("topic") or ""),
        grade=str(context.get("grade") or model.get("grade") or ""),
        lesson_excerpt=(context.get("lesson_text") or "")[:2000],
        concept_ids=[c for c in concept_ids if c],
        learning_objectives=[x for x in los if x][:8],
        mastery_level=mastery,
        misconceptions=list(ame.get("misconceptions") or ale.get("misconceptions") or [])[:8],
        accessibility_profiles=list(profiles),
        presentation_mode=str(presentation),
        reading_level=str(reading),
        pathway=ale.get("learning_path") or {},
        confidence=conf,
        goals=list((ale.get("day_plan") or {}).get("goals") or context.get("goals") or []),
        teacher_mode_override=context.get("tutor_mode_override") or context.get("teacher_tutor_mode"),
        allow_direct_answers=bool(context.get("allow_direct_answers", True)),
        require_socratic=bool(context.get("require_socratic", False)),
    )
