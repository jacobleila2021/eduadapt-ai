"""Parent analytics — progress for home support (no medical inferences)."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.learner_analytics import learner_analytics


def parent_analytics(sources: dict[str, Any]) -> dict[str, Any]:
    learner = learner_analytics(sources)
    ale = sources.get("ale") or {}
    aie = sources.get("aie") or {}
    progress = learner.get("learning_progress") or {}

    strengths = progress.get("mastered") or []
    needs = progress.get("at_risk") or []
    return {
        "learner_id": learner.get("learner_id"),
        "progress_summary": {
            "mastered": len(strengths),
            "needs_support": len(needs),
            "confidence": learner.get("learning_confidence"),
            "exam_readiness": (learner.get("assessment_history") or {}).get("exam_readiness"),
        },
        "learning_strengths": strengths[:8],
        "areas_needing_support": needs[:8],
        "reading_habits": learner.get("reading_behaviour") or {},
        "homework_completion": (learner.get("study_consistency") or {}).get("completion_rate"),
        "accessibility_supports": (learner.get("accessibility_usage") or {}).get("profiles") or [],
        "achievement_timeline": (sources.get("gamification") or {}).get("badges") or [],
        "suggested_home_activities": (ale.get("recommendations") or {}).get("parent")
        or [
            {"detail": "Short official-bank practice (5–10 min)", "priority": 1},
            {"detail": "Use TTS/read-aloud if reading support is enabled", "priority": 2},
        ],
        "encouragement_tips": [
            "Celebrate small mastery gains — progress over perfection.",
            "Keep sessions short if attention support is active.",
            "Ask the learner to explain one concept in their own words.",
        ],
        "interface_summary": aie.get("interface") or {},
        "policy": "no_medical_diagnoses_functional_supports_only",
    }
