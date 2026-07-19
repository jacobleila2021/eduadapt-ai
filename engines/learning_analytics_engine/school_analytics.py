"""School / department analytics."""

from __future__ import annotations

from typing import Any

from engines.learning_analytics_engine.class_analytics import class_analytics


def school_analytics(
    class_source_groups: list[dict[str, Any]] | None = None,
    *,
    single_sources: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if class_source_groups:
        classes = []
        for g in class_source_groups:
            bundle = class_analytics(g.get("learners") or [])
            classes.append({"class_id": g.get("class_id"), **bundle})
        total = sum(c.get("class_size") or 0 for c in classes)
        return {
            "school_wide_mastery": classes,
            "department_dashboards": classes,
            "curriculum_coverage": "aggregate_from_cie_per_class",
            "assessment_quality": {"policy": "official_bank"},
            "accessibility_compliance": {"wcag_target": "WCAG 2.2 AA"},
            "teacher_workload": {"note": "Hook to roster/assignments when available"},
            "intervention_success": {"note": "Longitudinal AME comparison"},
            "student_engagement": {"learners_total": total},
            "attendance_integration_hooks": ["sis_attendance_id", "lms_presence"],
            "strategic_recommendations": [
                "Prioritize classes with highest at-risk counts for reteach blocks",
                "Audit accessibility adoption vs WCAG 2.2 AA checklist",
            ],
        }

    src = single_sources or {}
    bundle = class_analytics([src] if src else [])
    cie = src.get("cie") or {}
    return {
        "school_wide_mastery": bundle,
        "department_dashboards": [{"class_id": "pilot", **bundle}],
        "curriculum_coverage": cie.get("graph_stats") or {},
        "assessment_quality": {"official_items": len((src.get("ame") or {}).get("official_mcqs") or [])},
        "accessibility_compliance": {
            "wcag_target": "WCAG 2.2 AA",
            "profiles": bundle.get("accessibility_profile_distribution"),
        },
        "teacher_workload": {},
        "intervention_success": {},
        "student_engagement": {"class_size": bundle.get("class_size")},
        "attendance_integration_hooks": ["sis_attendance_id", "lms_presence"],
        "strategic_recommendations": [
            "Expand Class 8 Science pilot analytics to additional chapters",
        ],
    }
