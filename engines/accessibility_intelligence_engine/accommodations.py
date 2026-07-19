"""Recommendation + accommodation application — presentation only."""

from __future__ import annotations

from typing import Any

from engines.accessibility_intelligence_engine.adaptation_rules import (
    apply_rules,
    catalog_supports,
    specs_for_profiles,
)
from engines.accessibility_intelligence_engine.schemas import (
    AccessibilityRecommendation,
    LearnerAccessibilityProfile,
)


def generate_recommendations(profile: LearnerAccessibilityProfile) -> list[AccessibilityRecommendation]:
    recs = apply_rules(profile.active_profiles)
    # Teacher/parent accommodations as high-priority evidence
    for i, acc in enumerate(profile.teacher_accommodations or []):
        recs.append(
            AccessibilityRecommendation(
                support_id=f"teacher_{i}",
                category="assessment",
                title=f"Teacher accommodation: {acc}",
                reason="Teacher-assigned accommodation",
                evidence="teacher_accommodations",
                priority=5,
                expected_impact="high",
                confidence=0.95,
            )
        )
    for i, acc in enumerate(profile.parent_accommodations or []):
        recs.append(
            AccessibilityRecommendation(
                support_id=f"parent_{i}",
                category="sensory",
                title=f"Parent-requested support: {acc}",
                reason="Family-requested functional support",
                evidence="parent_accommodations",
                priority=25,
                expected_impact="medium",
                confidence=0.8,
            )
        )
    recs.sort(key=lambda r: r.priority)
    return recs


def apply_accommodations(
    profile: LearnerAccessibilityProfile,
    *,
    cie_adaptations: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Produce accommodation package for lessons/assessments.
    Never alters curriculum facts or official answers.
    """
    recs = generate_recommendations(profile)
    specs = specs_for_profiles(profile.active_profiles)
    supports = catalog_supports(profile.active_profiles)
    ame_profiles = []
    for p in profile.active_profiles:
        # AME uses shorter keys
        if p == "executive_function":
            ame_profiles.append("executive_function")
        else:
            ame_profiles.append(p)

    assessment_accommodations = []
    support_ids = {r.support_id for r in recs}
    if "task_chunking" in support_ids or "adhd" in profile.active_profiles:
        assessment_accommodations.extend(["chunked_items", "progress_checklist"])
    if "dyslexia" in profile.active_profiles or "ell" in profile.active_profiles:
        assessment_accommodations.extend(["extra_time_factor_1.5", "glossary_support", "dyslexia_friendly_font_hint"])
    if "dyscalculia" in profile.active_profiles:
        assessment_accommodations.extend(["formula_card_allowed", "concrete_examples", "no_timed_drills"])
    if "autism" in profile.active_profiles:
        assessment_accommodations.extend(["predictable_item_order", "explicit_success_criteria"])
    if "gifted" in profile.active_profiles or "twice_exceptional" in profile.active_profiles:
        assessment_accommodations.append("extension_hots_optional")
    if "motor" in profile.active_profiles:
        assessment_accommodations.append("keyboard_only_navigation")

    return {
        "learner_id": profile.learner_id,
        "active_profiles": list(profile.active_profiles),
        "prioritized_adaptation_specs": specs,
        "functional_supports": supports,
        "recommendations": [r.to_dict() for r in recs],
        "assessment_accommodations": list(dict.fromkeys(assessment_accommodations)),
        "accessibility_profiles_for_ame": ame_profiles,
        "cie_presentation_hints": cie_adaptations or {},
        "policy": {
            "presentation_only": True,
            "curriculum_facts_locked": True,
            "official_answers_locked": True,
            "no_medical_diagnoses_stored": True,
            "wcag_target": "WCAG 2.2 AA",
            "udl": "UDL 3.0",
        },
    }
