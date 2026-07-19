"""Learner-level analytics — progress, mastery, engagement signals."""

from __future__ import annotations

from typing import Any


def learner_analytics(sources: dict[str, Any]) -> dict[str, Any]:
    cie = sources.get("cie") or {}
    ame = sources.get("ame") or {}
    aie = sources.get("aie") or {}
    ale = sources.get("ale") or {}
    tutor = sources.get("tutor") or {}
    game = sources.get("gamification") or {}
    lesson = sources.get("lesson") or {}
    reader = (sources.get("context") or {}).get("lesson_reader") or {}
    model = ale.get("learner_model") or {}
    mastery = ame.get("mastery") or {}
    conf = ale.get("confidence") or ame.get("exam_readiness") or {}

    mastered = model.get("concepts_mastered") or []
    developing = model.get("concepts_developing") or []
    at_risk = model.get("concepts_at_risk") or mastery.get("weak_concepts") or []
    if at_risk and isinstance(at_risk[0], dict):
        at_risk = [x.get("concept_id") for x in at_risk]

    return {
        "learner_id": (sources.get("context") or {}).get("learner_id"),
        "learning_progress": {
            "mastered_count": len(mastered),
            "developing_count": len(developing),
            "at_risk_count": len(at_risk) if isinstance(at_risk, list) else 0,
            "mastered": mastered,
            "developing": developing,
            "at_risk": at_risk,
        },
        "mastery_growth": mastery.get("by_level") or {},
        "curriculum_coverage": {
            "matched_concepts": len(cie.get("matched_concepts") or []),
            "learning_outcomes": len(cie.get("learning_outcomes") or []),
            "primary_concept_id": cie.get("primary_concept_id"),
        },
        "competency_progression": cie.get("competencies") or ame.get("cie_bindings", {}).get("competencies") or [],
        "accessibility_usage": {
            "profiles": (aie.get("learner_profile") or {}).get("active_profiles")
            or aie.get("profiles_generated")
            or model.get("accessibility_profiles")
            or [],
            "supports": (aie.get("accommodations") or {}).get("functional_supports") or [],
            "interface": aie.get("interface") or {},
        },
        "reading_behaviour": {
            "lesson_reading_level": lesson.get("reading_level"),
            "complexity_score": lesson.get("complexity_score"),
            "reader_time_sec": reader.get("reading_time_sec"),
            "scroll_depth": reader.get("scroll_depth"),
            "bookmarks": reader.get("bookmarks") or [],
            "notes_count": reader.get("notes_count") or 0,
            "focus_mode": reader.get("focus_mode"),
            "tts_usage": reader.get("tts_usage"),
            "completion": reader.get("completion"),
        },
        "assessment_history": {
            "exam_readiness": ame.get("exam_readiness") or {},
            "misconceptions": ame.get("misconceptions") or ale.get("misconceptions") or [],
            "revision_plan": ame.get("revision_plan") or {},
        },
        "learning_confidence": conf,
        "engagement": {
            "next_activity": ale.get("next_activity") or {},
            "pathway_type": (ale.get("learning_path") or {}).get("pathway_type"),
            "streaks": (game.get("streaks") or {}),
            "xp": game.get("xp"),
        },
        "motivation": {
            "quests": game.get("quests") or [],
            "badges": game.get("badges") or [],
            "motivation_level": model.get("motivation_level"),
        },
        "study_consistency": {
            "learning_streak": model.get("learning_streak") or (game.get("streaks") or {}).get("days") or 0,
            "completion_rate": model.get("completion_rate"),
        },
        "ai_tutor_interactions": {
            "modes": tutor.get("modes") or [],
            "verified_artifact_count": tutor.get("verified_artifact_count"),
            "adaptive_brief": tutor.get("adaptive_brief") or tutor.get("accessibility_profile") or {},
        },
        "recommended_next_steps": (ale.get("recommendations") or {}).get("student")
        or (ame.get("revision_plan") or {}).get("priority_topics")
        or [],
        "risk_indicators": ale.get("predictions") or {},
        "lesson_metadata": lesson,
        "philosophy": {
            "what": "Aggregated learner state from verified engines",
            "why": "Evidence from AME/CIE/AIE/ALE — not LLM invention",
            "policy": "insights_only_no_content_mutation",
        },
    }
