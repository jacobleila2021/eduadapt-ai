"""Assessment & Mastery intelligence — orchestrates AME modules for VLIE."""

from __future__ import annotations

from typing import Any

from engines.assessment_mastery_engine.adaptive import adaptive_assessment
from engines.assessment_mastery_engine.assessments import generate_assessment
from engines.assessment_mastery_engine.exam_readiness import exam_readiness
from engines.assessment_mastery_engine.indexing import rebuild_ame_index
from engines.assessment_mastery_engine.interventions import resolve_interventions
from engines.assessment_mastery_engine.mastery import mastery_summary, recompute_all_mastery
from engines.assessment_mastery_engine.misconceptions import detect_from_text
from engines.assessment_mastery_engine.revision import generate_revision_plan


def _cie_from_context(context: dict[str, Any]) -> dict[str, Any]:
    curr = (context.get("engine_outputs") or {}).get("curriculum") or {}
    payload = curr.get("payload") if isinstance(curr, dict) else {}
    if not isinstance(payload, dict):
        return {}
    return payload.get("curriculum_intelligence") or {}


def _bank_payload(context: dict[str, Any]) -> dict[str, Any]:
    """Reuse existing official bank / exam bundle path (no duplication)."""
    from knowledge.question_bank import match_exam_bundle
    from knowledge.question_rag import get_question_index, semantic_match_questions

    topic = context.get("topic") or ""
    lesson = context.get("lesson_text") or ""
    curr = (context.get("engine_outputs") or {}).get("curriculum") or {}
    knowledge = (curr.get("payload") or {}).get("knowledge") if isinstance(curr, dict) else {}
    if isinstance(knowledge, dict) and knowledge.get("exam_bundle"):
        return {
            "official_mcqs": knowledge.get("official_mcqs") or [],
            "exam_bundle": knowledge["exam_bundle"],
            "index": {"from": "curriculum_stage"},
        }
    idx = get_question_index()
    idx_info = idx.ensure_index()
    matched = semantic_match_questions(topic, lesson, limit=8)
    official = [
        {
            "item_id": it.item_id,
            "source": it.source,
            "question": it.question,
            "official_answer": it.official_answer,
            "bloom": it.bloom,
            "marks": it.marks,
            "topic": it.topic,
            "chapter": it.chapter,
        }
        for it in matched
    ]
    bundle_raw = match_exam_bundle(topic, limit_per_type=2)
    bundle = {
        k: [
            {
                "item_id": it.item_id,
                "source": it.source,
                "question": it.question,
                "official_answer": it.official_answer,
                "bloom": it.bloom,
                "marks": it.marks,
            }
            for it in v
        ]
        for k, v in bundle_raw.items()
    }
    return {"official_mcqs": official, "exam_bundle": bundle, "index": idx_info}


def analyze_assessment_context(context: dict[str, Any]) -> dict[str, Any]:
    """
    Full AME enrichment for AssessmentEngine / VLIE.
    Preserves official bank retrieval; adds mastery intelligence.
    """
    learner_id = context.get("learner_id") or context.get("student_id") or "anonymous"
    topic = context.get("topic") or ""
    lesson = context.get("lesson_text") or ""
    profiles = context.get("accessibility_profiles") or []
    cie = _cie_from_context(context)
    bank = _bank_payload(context)

    # Detect misconceptions from lesson + topic text (pre-instruction diagnostic signal)
    concept_ids = [c.get("concept_id") for c in (cie.get("matched_concepts") or []) if c.get("concept_id")]
    misc_hits = detect_from_text(f"{topic}\n{lesson}", concept_ids=concept_ids or None)
    interventions = [r.to_dict() for r in resolve_interventions(misc_hits, accessibility_profiles=profiles)]

    assessment_type = context.get("assessment_type") or "formative"
    if context.get("adaptive"):
        assessment = adaptive_assessment(
            learner_id=learner_id,
            topic=topic,
            lesson_text=lesson,
            concept_id=(concept_ids[0] if concept_ids else ""),
            accessibility_profiles=profiles,
            cie_context=cie,
        )
    else:
        assessment = generate_assessment(
            assessment_type=assessment_type,
            topic=topic,
            lesson_text=lesson,
            concept_ids=concept_ids,
            learner_id=learner_id,
            cie_context=cie,
        )

    mastery = {}
    revision = {}
    readiness = {}
    if learner_id and learner_id != "anonymous":
        recompute_all_mastery(learner_id)
        mastery = mastery_summary(learner_id)
        revision = generate_revision_plan(
            learner_id,
            topic=topic,
            exam_days=context.get("exam_days"),
            accessibility_profiles=profiles,
            cie_context=cie,
        )
        readiness = exam_readiness(learner_id, topic=topic, concept_ids=concept_ids, cie_context=cie)

    return {
        **bank,
        "mastery_hooks": ["retrieve", "practice", "reflect", "remediate", "reassess"],
        "assessment_package": assessment,
        "misconceptions": [h.to_dict() for h in misc_hits],
        "interventions": interventions,
        "mastery": mastery,
        "revision_plan": revision,
        "exam_readiness": readiness,
        "cie_bindings": {
            "primary_concept_id": cie.get("primary_concept_id"),
            "learning_outcomes": cie.get("learning_outcomes") or [],
            "competencies": cie.get("competencies") or [],
            "prerequisites": cie.get("prerequisites") or {},
        },
        "learner_id": learner_id,
        "policy": {
            "official_answers_only": True,
            "multi_evidence_mastery": True,
            "wraps_question_bank": True,
            "integrates_cie": True,
            "does_not_invent_keys": True,
        },
    }


def ensure_indexed(force: bool = False) -> dict[str, Any]:
    return rebuild_ame_index()
