"""Domain analysis modules — curriculum, mastery, accessibility, engagement, tutor, interventions."""

from __future__ import annotations

from collections import Counter
from typing import Any


def curriculum_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    cie = sources.get("cie") or {}
    outcomes = cie.get("learning_outcomes") or []
    blooms = Counter((o.get("bloom") if isinstance(o, dict) else None) or "unknown" for o in outcomes)
    doks = Counter(str((o.get("dok") if isinstance(o, dict) else None) or "") for o in outcomes)
    return {
        "coverage_by_curriculum": cie.get("curriculum_ref") or {},
        "coverage_by_standard": outcomes,
        "bloom_distribution": dict(blooms),
        "dok_distribution": dict(doks),
        "competency_completion": cie.get("competencies") or [],
        "prerequisite_completion": cie.get("prerequisites") or cie.get("learning_gaps") or {},
        "concept_mastery_bindings": cie.get("matched_concepts") or [],
        "knowledge_gaps": cie.get("learning_gaps") or {},
    }


def mastery_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    ame = sources.get("ame") or {}
    ale = sources.get("ale") or {}
    return {
        "mastery_summary": ame.get("mastery") or {},
        "learner_model_bands": {
            "mastered": (ale.get("learner_model") or {}).get("concepts_mastered"),
            "developing": (ale.get("learner_model") or {}).get("concepts_developing"),
            "at_risk": (ale.get("learner_model") or {}).get("concepts_at_risk"),
        },
        "exam_readiness": ame.get("exam_readiness") or {},
        "revision_effectiveness": {
            "plan": ame.get("revision_plan") or {},
            "spaced_repetition": ale.get("spaced_repetition") or [],
        },
        "growth_over_time": {"note": "Compare sequential AME mastery snapshots"},
    }


def accessibility_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    aie = sources.get("aie") or {}
    iface = aie.get("interface") or {}
    reader = (sources.get("context") or {}).get("lesson_reader") or {}
    return {
        "font_usage": iface.get("font"),
        "theme_usage": iface.get("colour_theme"),
        "tts_usage": reader.get("tts_usage") or ("tts_enabled" in str(aie.get("accommodations"))),
        "reading_ruler": iface.get("reading_ruler"),
        "focus_mode": iface.get("focus_mode") or reader.get("focus_mode"),
        "spacing_preferences": {
            "line": iface.get("line_spacing"),
            "paragraph": iface.get("paragraph_spacing"),
        },
        "accommodation_effectiveness": {
            "supports": (aie.get("accommodations") or {}).get("functional_supports") or [],
            "note": "Correlate support usage with mastery deltas longitudinally",
        },
        "support_adoption": (aie.get("learner_profile") or {}).get("active_profiles") or aie.get("profiles_generated"),
        "wcag_compliance_metrics": {
            "target": aie.get("wcag_target") or "WCAG 2.2 AA",
            "udl": aie.get("udl"),
            "facts_immutable": aie.get("facts_immutable"),
        },
    }


def engagement_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    game = sources.get("gamification") or {}
    ale = sources.get("ale") or {}
    reader = (sources.get("context") or {}).get("lesson_reader") or {}
    model = ale.get("learner_model") or {}
    return {
        "daily_activity": reader.get("daily_activity") or {},
        "weekly_activity": reader.get("weekly_activity") or {},
        "monthly_activity": reader.get("monthly_activity") or {},
        "session_length": reader.get("reading_time_sec") or model.get("time_on_task_min"),
        "learning_streaks": game.get("streaks") or {"days": model.get("learning_streak") or 0},
        "xp_growth": game.get("xp") or 0,
        "quest_completion": game.get("quests") or [],
        "motivation_trends": model.get("motivation_level"),
        "consistency": model.get("completion_rate"),
    }


def ai_tutor_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    tutor = sources.get("tutor") or {}
    return {
        "questions_asked": tutor.get("questions_asked"),
        "hints_requested": tutor.get("hints_requested"),
        "conversation_length": tutor.get("conversation_length"),
        "concept_confusion": tutor.get("misconception_hooks") or [],
        "help_seeking_behaviour": tutor.get("modes") or [],
        "confidence_growth": (sources.get("ale") or {}).get("confidence") or {},
        "response_effectiveness": {
            "grounding": tutor.get("grounding"),
            "verified_artifact_count": tutor.get("verified_artifact_count"),
        },
        "session_history": tutor.get("session_history") or [],
    }


def intervention_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    ale = sources.get("ale") or {}
    ame = sources.get("ame") or {}
    return {
        "active_interventions": ale.get("interventions") or ame.get("interventions") or [],
        "enrichment": ale.get("enrichment") or [],
        "teacher_recs": (ale.get("recommendations") or {}).get("teacher") or [],
        "success_tracking": {"note": "Compare mastery before/after intervention_id in AME evidence"},
    }


# Thin module files expected by prompt — re-export domain functions
def assessment_side_analysis(sources: dict[str, Any]) -> dict[str, Any]:
    ame = sources.get("ame") or {}
    misc = ame.get("misconceptions") or []
    return {
        "question_difficulty": "derived_from_item_metadata_when_attempts_exist",
        "distractor_effectiveness": "requires_option_level_attempt_logs",
        "common_misconceptions": misc,
        "mastery_trends": ame.get("mastery") or {},
        "revision_effectiveness": ame.get("revision_plan") or {},
        "assessment_reliability": {"policy": "official_bank_keys_only"},
        "growth_over_time": {"note": "Snapshot AME mastery_pct series"},
    }
