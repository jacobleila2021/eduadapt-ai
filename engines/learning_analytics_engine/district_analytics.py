"""District analytics — aggregated comparisons."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.school_analytics import school_analytics


def district_analytics(school_bundles: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    schools = school_bundles or [school_analytics(single_sources={})]
    return {
        "school_comparisons": [
            {
                "school_index": i,
                "engagement": s.get("student_engagement"),
                "accessibility": s.get("accessibility_compliance"),
            }
            for i, s in enumerate(schools)
        ],
        "curriculum_implementation": {"note": "Compare CIE coverage ratios across schools"},
        "accessibility_adoption": [s.get("accessibility_compliance") for s in schools],
        "intervention_success": [s.get("intervention_success") for s in schools],
        "achievement_trends": {"note": "Requires longitudinal mastery snapshots"},
        "resource_utilization": {"note": "Bank items / tutor sessions / TTS usage"},
        "policy_insights": [
            "Keep educators in control of interventions",
            "Aggregate-only views for district roles — no student PII in exports by default",
        ],
        "benchmark_dashboards": schools,
    }
