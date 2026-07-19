"""Executive / enterprise / government summary views."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.district_analytics import district_analytics
from engines.learning_analytics_engine.school_analytics import school_analytics


def executive_analytics(sources: dict[str, Any] | None = None) -> dict[str, Any]:
    school = school_analytics(single_sources=sources or {})
    district = district_analytics([school])
    return {
        "executive_summary": {
            "platform": "Alora AI Verified Learning Intelligence",
            "pilot_focus": "CBSE/NCERT Class 8 Science",
            "engines_integrated": ["VLIE", "KIE", "CIE", "AME", "AIE", "ALE", "LAIE"],
            "key_signals": {
                "assessment_quality": school.get("assessment_quality"),
                "accessibility_compliance": school.get("accessibility_compliance"),
                "strategic_recommendations": school.get("strategic_recommendations"),
            },
        },
        "enterprise": {
            "tenancy_ready": False,
            "note": "School tenancy / SSO deferred — analytics schema is multi-tenant ready",
        },
        "government": {
            "aggregate_only": True,
            "benchmarks": district.get("benchmark_dashboards"),
            "policy_insights": district.get("policy_insights"),
        },
        "investor_demo": {
            "message": "Evidence-based learning OS: verified knowledge → adaptive decisions → explainable analytics",
            "moat": ["KIE", "CIE", "AME", "AIE", "ALE", "LAIE"],
        },
    }
