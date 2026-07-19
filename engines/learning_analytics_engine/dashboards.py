"""Role dashboards — data payloads (UI filters/exports/a11y applied at presentation layer)."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.accessibility_analysis import accessibility_analysis
from engines.learning_analytics_engine.ai_tutor_analysis import ai_tutor_analysis
from engines.learning_analytics_engine.class_analytics import class_analytics
from engines.learning_analytics_engine.curriculum_analysis import curriculum_analysis
from engines.learning_analytics_engine.district_analytics import district_analytics
from engines.learning_analytics_engine.engagement_analysis import engagement_analysis
from engines.learning_analytics_engine.executive_analytics import executive_analytics
from engines.learning_analytics_engine.learner_analytics import learner_analytics
from engines.learning_analytics_engine.mastery_analysis import mastery_analysis
from engines.learning_analytics_engine.parent_analytics import parent_analytics
from engines.learning_analytics_engine.predictive_models import predictive_insights
from engines.learning_analytics_engine.recommendations import build_insight_recommendations
from engines.learning_analytics_engine.school_analytics import school_analytics
from engines.learning_analytics_engine.special_educator_analytics import special_educator_analytics
from engines.learning_analytics_engine.teacher_analytics import teacher_analytics
from engines.learning_analytics_engine.alerts import generate_alerts


def dashboard_for_role(role: str, sources: dict[str, Any], *, learner_ids_sources: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    role = (role or "student").lower()
    common = {
        "filters_supported": ["topic", "grade", "date_range", "profile"],
        "exports_supported": ["json", "csv", "excel", "pdf"],
        "accessibility": {"wcag": "WCAG 2.2 AA", "responsive": True, "dark_mode_ready": True, "print_ready": True},
        "alerts": generate_alerts(sources),
        "recommendations": build_insight_recommendations(sources),
        "predictions": predictive_insights(sources),
    }

    if role == "student":
        return {"role": "student", "dashboard": learner_analytics(sources), **common}
    if role == "parent":
        return {"role": "parent", "dashboard": parent_analytics(sources), **common}
    if role == "special_educator":
        return {"role": "special_educator", "dashboard": special_educator_analytics(sources), **common}
    if role == "teacher":
        bundle = class_analytics(learner_ids_sources or [sources])
        return {
            "role": "teacher",
            "dashboard": teacher_analytics(sources, bundle),
            "class": bundle,
            **common,
        }
    if role == "school":
        return {"role": "school", "dashboard": school_analytics(single_sources=sources), **common}
    if role == "district":
        return {"role": "district", "dashboard": district_analytics([school_analytics(single_sources=sources)]), **common}
    if role in ("administrator", "enterprise", "government"):
        return {"role": role, "dashboard": executive_analytics(sources), **common}

    return {
        "role": role,
        "dashboard": {
            "learner": learner_analytics(sources),
            "curriculum": curriculum_analysis(sources),
            "mastery": mastery_analysis(sources),
            "accessibility": accessibility_analysis(sources),
            "engagement": engagement_analysis(sources),
            "tutor": ai_tutor_analysis(sources),
        },
        **common,
    }
