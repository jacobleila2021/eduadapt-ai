"""Special educator analytics — accommodation & intervention effectiveness."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.learner_analytics import learner_analytics


def special_educator_analytics(sources: dict[str, Any]) -> dict[str, Any]:
    learner = learner_analytics(sources)
    aie = sources.get("aie") or {}
    ale = sources.get("ale") or {}
    accommodations = aie.get("accommodations") or {}
    return {
        "learner_id": learner.get("learner_id"),
        "accommodation_usage": {
            "profiles": (learner.get("accessibility_usage") or {}).get("profiles"),
            "supports": accommodations.get("functional_supports") or [],
            "assessment_accommodations": accommodations.get("assessment_accommodations") or [],
            "recommendations": accommodations.get("recommendations") or [],
        },
        "intervention_effectiveness": {
            "assigned": ale.get("interventions") or (sources.get("ame") or {}).get("interventions") or [],
            "note": "Track pre/post mastery_pct via AME evidence over time",
        },
        "executive_function_progress": aie.get("executive_function_supports") or {},
        "reading_improvements": {
            "readability": aie.get("readability") or {},
            "lesson_level": (sources.get("lesson") or {}).get("reading_level"),
        },
        "support_effectiveness": {
            "assistive_tech": aie.get("assistive_technology") or [],
            "language_support": aie.get("language_support") or {},
        },
        "student_goals": (ale.get("day_plan") or {}).get("goals") or [],
        "recommended_accommodations": accommodations.get("recommendations") or [],
        "progress_over_time": learner.get("learning_progress") or {},
        "policy": "functional_supports_only_no_medical_diagnoses",
    }
