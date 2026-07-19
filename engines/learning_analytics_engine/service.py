"""REST-shaped API facade for Learning Analytics & Insights Engine."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine._sources import collect_sources
from engines.learning_analytics_engine.alerts import generate_alerts
from engines.learning_analytics_engine.dashboards import dashboard_for_role
from engines.learning_analytics_engine.district_analytics import district_analytics
from engines.learning_analytics_engine.engagement_analysis import engagement_analysis
from engines.learning_analytics_engine.indexing import rebuild_laie_index
from engines.learning_analytics_engine.intelligence import analyze_insights
from engines.learning_analytics_engine.learner_analytics import learner_analytics
from engines.learning_analytics_engine.parent_analytics import parent_analytics
from engines.learning_analytics_engine.predictive_models import predictive_insights
from engines.learning_analytics_engine.recommendations import build_insight_recommendations
from engines.learning_analytics_engine.reporting import build_report
from engines.learning_analytics_engine.school_analytics import school_analytics
from engines.learning_analytics_engine.teacher_analytics import teacher_analytics
from engines.learning_analytics_engine.accessibility_analysis import accessibility_analysis


def _ctx(**kwargs: Any) -> dict[str, Any]:
    return kwargs


def api_learner_analytics(**kwargs: Any) -> dict[str, Any]:
    return learner_analytics(collect_sources(_ctx(**kwargs)))


def api_teacher_analytics(**kwargs: Any) -> dict[str, Any]:
    return teacher_analytics(collect_sources(_ctx(**kwargs)))


def api_parent_analytics(**kwargs: Any) -> dict[str, Any]:
    return parent_analytics(collect_sources(_ctx(**kwargs)))


def api_school_analytics(**kwargs: Any) -> dict[str, Any]:
    return school_analytics(single_sources=collect_sources(_ctx(**kwargs)))


def api_district_analytics(**kwargs: Any) -> dict[str, Any]:
    school = school_analytics(single_sources=collect_sources(_ctx(**kwargs)))
    return district_analytics([school])


def api_predictive_insights(**kwargs: Any) -> dict[str, Any]:
    return predictive_insights(collect_sources(_ctx(**kwargs)))


def api_intervention_recommendations(**kwargs: Any) -> dict[str, Any]:
    return {"recommendations": build_insight_recommendations(collect_sources(_ctx(**kwargs)))}


def api_engagement_metrics(**kwargs: Any) -> dict[str, Any]:
    return engagement_analysis(collect_sources(_ctx(**kwargs)))


def api_accessibility_metrics(**kwargs: Any) -> dict[str, Any]:
    return accessibility_analysis(collect_sources(_ctx(**kwargs)))


def api_reporting(report_type: str, **kwargs: Any) -> dict[str, Any]:
    fmt = kwargs.pop("fmt", "json")
    insights = analyze_insights(_ctx(**kwargs))
    mapping = {
        "student": insights.get("learner_analytics"),
        "parent": parent_analytics(collect_sources(_ctx(**kwargs))),
        "teacher": insights.get("teacher_analytics"),
        "progress": insights.get("mastery_analytics"),
        "curriculum": insights.get("curriculum_analytics"),
        "assessment": insights.get("assessment_analytics"),
        "accessibility": insights.get("accessibility_analytics"),
        "executive": insights.get("predictions"),
        "investor": {"engines": ["VLIE", "KIE", "CIE", "AME", "AIE", "ALE", "LAIE"], "insights": True},
        "iep_support": {
            "accessibility": insights.get("accessibility_analytics"),
            "note": "Functional supports only — not a medical IEP document",
        },
    }
    payload = mapping.get(report_type) or insights
    return build_report(report_type, payload, learner_id=kwargs.get("learner_id") or "", fmt=fmt)


def api_dashboard_summaries(role: str = "student", **kwargs: Any) -> dict[str, Any]:
    return dashboard_for_role(role, collect_sources(_ctx(**kwargs)))


def api_alerts(**kwargs: Any) -> dict[str, Any]:
    return {"alerts": generate_alerts(collect_sources(_ctx(**kwargs)), thresholds=kwargs.get("alert_thresholds"))}


def api_analyze_context(context: dict[str, Any]) -> dict[str, Any]:
    return analyze_insights(context)


def api_rebuild_index() -> dict[str, Any]:
    return rebuild_laie_index()
