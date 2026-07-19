"""Accessibility dashboards — teacher / parent / student (data payloads)."""

from __future__ import annotations

from typing import Any

from engines.accessibility_intelligence_engine.analytics import analytics_summary
from engines.accessibility_intelligence_engine.learner_profile import list_profile_ids, load_profile
from engines.accessibility_intelligence_engine.accommodations import apply_accommodations, generate_recommendations
from engines.accessibility_intelligence_engine.interface import build_interface_config, interface_css_hints
from engines.accessibility_intelligence_engine.presentation import select_presentation_mode


def student_dashboard(learner_id: str) -> dict[str, Any]:
    profile = load_profile(learner_id)
    cfg = build_interface_config(profile)
    return {
        "role": "student",
        "learner_id": learner_id,
        "active_profiles": profile.active_profiles,
        "customizable": {
            "font": True,
            "colours": True,
            "spacing": True,
            "audio": True,
            "focus_mode": True,
            "preview_themes": ["default", "cream_soft", "high_contrast", "calm", "cvd_safe"],
            "reset_to_defaults": True,
        },
        "current_settings": cfg.to_dict(),
        "css_hints": interface_css_hints(cfg),
        "presentation": select_presentation_mode(profile),
        "analytics": analytics_summary(learner_id),
    }


def teacher_dashboard(learner_id: str) -> dict[str, Any]:
    profile = load_profile(learner_id)
    package = apply_accommodations(profile)
    return {
        "role": "teacher",
        "learner_id": learner_id,
        "recommended_accommodations": package["recommendations"],
        "supports_applied": package["functional_supports"],
        "assessment_accommodations": package["assessment_accommodations"],
        "manual_overrides": profile.teacher_accommodations,
        "accommodation_history": profile.accessibility_history[-20:],
        "insights": analytics_summary(learner_id),
        "suggested_improvements": [
            r.to_dict() if hasattr(r, "to_dict") else r
            for r in generate_recommendations(profile)[:5]
        ],
        "policy": package["policy"],
    }


def parent_dashboard(learner_id: str) -> dict[str, Any]:
    profile = load_profile(learner_id)
    mode = select_presentation_mode(profile)
    return {
        "role": "parent",
        "learner_id": learner_id,
        "current_supports": profile.active_profiles,
        "parent_accommodations": profile.parent_accommodations,
        "presentation_mode": mode.get("primary_mode"),
        "home_learning_tips": [
            "Keep sessions short if attention support is enabled.",
            "Use read-aloud / TTS when reading support is on.",
            "Prefer official practice items for homework — do not invent answers.",
        ],
        "accessibility_settings_summary": build_interface_config(profile).to_dict(),
        "progress_note": "Join AME mastery dashboard for academic progress; AIE shows supports only.",
    }


def class_overview(learner_ids: list[str] | None = None) -> dict[str, Any]:
    ids = learner_ids or list_profile_ids()
    rows = []
    for lid in ids:
        p = load_profile(lid)
        rows.append(
            {
                "learner_id": lid,
                "profiles": p.active_profiles,
                "teacher_overrides": len(p.teacher_accommodations or []),
            }
        )
    return {"role": "teacher_class", "learners": rows, "count": len(rows)}
