"""LAIE intelligence — orchestrate insights for VLIE LearningAnalyticsEngine."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine._sources import collect_sources
from engines.learning_analytics_engine.accessibility_analysis import accessibility_analysis
from engines.learning_analytics_engine.ai_tutor_analysis import ai_tutor_analysis
from engines.learning_analytics_engine.alerts import generate_alerts
from engines.learning_analytics_engine.curriculum_analysis import assessment_side_analysis, curriculum_analysis
from engines.learning_analytics_engine.dashboards import dashboard_for_role
from engines.learning_analytics_engine.engagement_analysis import engagement_analysis
from engines.learning_analytics_engine.indexing import rebuild_laie_index
from engines.learning_analytics_engine.intervention_analysis import intervention_analysis
from engines.learning_analytics_engine.learner_analytics import learner_analytics
from engines.learning_analytics_engine.mastery_analysis import mastery_analysis
from engines.learning_analytics_engine.predictive_models import predictive_insights
from engines.learning_analytics_engine.recommendations import build_insight_recommendations
from engines.learning_analytics_engine.teacher_analytics import teacher_analytics


def analyze_insights(context: dict[str, Any]) -> dict[str, Any]:
    """
    Full LAIE package.
    Never changes curriculum, answers, or accessibility decisions — insights only.
    """
    sources = collect_sources(context)
    role = (context.get("analytics_role") or "student").lower()

    learner = learner_analytics(sources)
    teacher = teacher_analytics(sources)
    predictions = predictive_insights(sources)
    recommendations = build_insight_recommendations(sources)
    alerts = generate_alerts(sources, thresholds=context.get("alert_thresholds"))

    # Philosophy answers
    what = {
        "lesson": sources.get("lesson"),
        "mastery": learner.get("learning_progress"),
        "engagement": learner.get("engagement"),
    }
    why = {
        "misconceptions": learner.get("assessment_history", {}).get("misconceptions"),
        "learning_gaps": (sources.get("cie") or {}).get("learning_gaps"),
        "explainability": (sources.get("ale") or {}).get("explainability"),
    }
    next_likely = predictions
    intervention = recommendations[:5]
    confidence = predictions.get("recommendation_confidence")
    evidence = predictions.get("explanatory_factors") or []

    dashboard = dashboard_for_role(role, sources)

    return {
        # Backward compatible with v1 LearningAnalyticsEngine
        "report": sources.get("lesson") or {},
        # LAIE enrichment
        "what_happened": what,
        "why_it_happened": why,
        "what_is_likely_next": next_likely,
        "recommended_intervention": intervention,
        "recommendation_confidence": confidence,
        "supporting_evidence": evidence,
        "learner_analytics": learner,
        "teacher_analytics": teacher,
        "curriculum_analytics": curriculum_analysis(sources),
        "mastery_analytics": mastery_analysis(sources),
        "assessment_analytics": assessment_side_analysis(sources),
        "accessibility_analytics": accessibility_analysis(sources),
        "engagement_analytics": engagement_analysis(sources),
        "ai_tutor_analytics": ai_tutor_analysis(sources),
        "intervention_analytics": intervention_analysis(sources),
        "predictions": predictions,
        "recommendations": recommendations,
        "alerts": alerts,
        "dashboard": dashboard,
        "role_views": {
            "student": dashboard_for_role("student", sources),
            "teacher": dashboard_for_role("teacher", sources),
            "parent": dashboard_for_role("parent", sources),
        },
        "policy": {
            "insights_only": True,
            "no_curriculum_mutation": True,
            "no_answer_mutation": True,
            "no_accessibility_override": True,
            "no_medical_diagnoses": True,
            "educator_final_authority": True,
            "explainable_auditable": True,
        },
        "laie_version": "2.0.0",
        "philosophy": [
            "What happened?",
            "Why did it happen?",
            "What is likely next?",
            "What intervention?",
            "How confident?",
            "Which evidence?",
        ],
    }


def ensure_indexed() -> dict[str, Any]:
    return rebuild_laie_index()
