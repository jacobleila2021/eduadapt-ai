"""REST-shaped API facade for Accessibility Intelligence Engine."""

from __future__ import annotations

from typing import Any

from engines.accessibility_intelligence_engine.accommodations import apply_accommodations, generate_recommendations
from engines.accessibility_intelligence_engine.analytics import analytics_summary, record_event
from engines.accessibility_intelligence_engine.dashboards import (
    class_overview,
    parent_dashboard,
    student_dashboard,
    teacher_dashboard,
)
from engines.accessibility_intelligence_engine.indexing import rebuild_aie_index
from engines.accessibility_intelligence_engine.intelligence import analyze_accessibility_context
from engines.accessibility_intelligence_engine.learner_profile import (
    load_profile,
    save_profile,
    update_preferences,
)
from engines.accessibility_intelligence_engine.readability import readability_report
from engines.accessibility_intelligence_engine.schemas import LearnerAccessibilityProfile


def api_get_learner_profile(learner_id: str) -> dict[str, Any]:
    return {"ok": True, "profile": load_profile(learner_id).to_dict()}


def api_update_accessibility_preferences(learner_id: str, updates: dict[str, Any]) -> dict[str, Any]:
    profile = update_preferences(learner_id, updates)
    return {"ok": True, "profile": profile.to_dict()}


def api_generate_recommendations(learner_id: str) -> dict[str, Any]:
    profile = load_profile(learner_id)
    recs = generate_recommendations(profile)
    return {"ok": True, "recommendations": [r.to_dict() for r in recs]}


def api_apply_accommodations(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    profile = load_profile(learner_id)
    if kwargs.get("accessibility_profiles"):
        profile.active_profiles = list(kwargs["accessibility_profiles"])
        save_profile(profile)
    return apply_accommodations(profile)


def api_get_readability_report(text: str) -> dict[str, Any]:
    return readability_report(text)


def api_retrieve_accessibility_analytics(learner_id: str) -> dict[str, Any]:
    return analytics_summary(learner_id)


def api_record_analytics_event(learner_id: str, event_type: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return record_event(learner_id, event_type, meta)


def api_analyze_context(context: dict[str, Any]) -> dict[str, Any]:
    return analyze_accessibility_context(context)


def api_rebuild_index() -> dict[str, Any]:
    return rebuild_aie_index()


def api_dashboards(role: str, learner_id: str = "", learner_ids: list[str] | None = None) -> dict[str, Any]:
    role = (role or "").lower()
    if role == "student":
        return student_dashboard(learner_id)
    if role == "parent":
        return parent_dashboard(learner_id)
    if role == "teacher":
        return teacher_dashboard(learner_id)
    if role == "class":
        return class_overview(learner_ids)
    return {"error": f"unknown role: {role}"}


def api_set_profiles(learner_id: str, profiles: list[str]) -> dict[str, Any]:
    profile = load_profile(learner_id)
    profile.active_profiles = list(profiles)
    save_profile(profile)
    return {"ok": True, "profile": profile.to_dict()}
