"""Lesson presentation mode selection — profile-driven, facts locked."""

from __future__ import annotations

from typing import Any

from engines.accessibility_intelligence_engine.adaptation_rules import PROFILE_TO_SPEC, normalize_profile_key
from engines.accessibility_intelligence_engine.schemas import LearnerAccessibilityProfile, PRESENTATION_MODES
from engines.accessibility_intelligence_engine.sensory_profiles import PROFILE_CATALOG


# Priority when multiple profiles compete (lower = stronger claim on primary mode)
_MODE_PRIORITY = {
    "blind": 1,
    "deaf": 2,
    "low_vision": 3,
    "dyslexia": 10,
    "adhd": 12,
    "autism": 13,
    "executive_function": 14,
    "dyscalculia": 15,
    "dysgraphia": 16,
    "ell": 18,
    "twice_exceptional": 20,
    "gifted": 25,
    "auditory": 30,
    "visual": 31,
    "multisensory": 32,
    "ld": 33,
    "professional": 40,
    "adult": 41,
    "neurotypical": 100,
}


def select_presentation_mode(profile: LearnerAccessibilityProfile) -> dict[str, Any]:
    profiles = [normalize_profile_key(p) for p in (profile.active_profiles or ["neurotypical"])]
    ranked = sorted(profiles, key=lambda p: _MODE_PRIORITY.get(p, 50))
    primary = ranked[0] if ranked else "neurotypical"
    catalog = PROFILE_CATALOG.get(primary) or {}
    mode = catalog.get("presentation") or PROFILE_TO_SPEC.get(primary) or "standard"
    if mode not in PRESENTATION_MODES and mode != "executive":
        mode = PROFILE_TO_SPEC.get(primary, "standard")

    secondary = [PROFILE_TO_SPEC.get(p, p) for p in ranked[1:4]]

    return {
        "primary_mode": mode,
        "secondary_modes": secondary,
        "all_modes_available": list(PRESENTATION_MODES),
        "rationale": f"Selected from functional profiles: {profiles}",
        "adaptation_spec_id": PROFILE_TO_SPEC.get(primary, "standard"),
        "multisensory": "multisensory" in profiles or mode == "multisensory",
        "policy": "presentation_selection_only",
    }


def presentation_presets_for_mode(mode: str) -> dict[str, Any]:
    """UI/content presentation hints consumed by toolbar / generators."""
    presets = {
        "standard": {"font": "system", "bullets": False, "grade_band": "on-level"},
        "dyslexia": {"font": "OpenDyslexic/Atkinson", "bullets": True, "grade_band": "3-4", "ruler": True},
        "adhd": {"chunk_minutes": 2, "checkpoints": True, "focus_mode": True},
        "autism": {"literal": True, "predictable_structure": True, "sensory_calm": True},
        "ell": {"glossary": True, "sentence_frames": True, "dual_language_ready": True},
        "dyscalculia": {"concrete_before_abstract": True, "no_timed_drills": True, "formula_cards": True},
        "dysgraphia": {"oral_or_typed": True, "scaffolded_writing": True},
        "executive": {"checklists": True, "step_by_step": True, "timers": True},
        "visual": {"diagrams_first": True, "concept_maps": True},
        "auditory": {"tts": True, "discussion_prompts": True},
        "gifted": {"extension": True, "depth": True},
        "multisensory": {"see_hear_do": True},
        "ld": {"scaffolds": True, "multisensory": True},
        "exam_revision": {"retrieval_practice": True, "official_bank": True},
        "parent_summary": {"plain_language": True, "home_tips": True},
        "teacher_guide": {"accommodation_map": True, "differentiation": True},
        "university": {"academic_register": True, "self_paced": True},
        "professional": {"concise": True, "just_in_time": True},
    }
    return presets.get(mode, presets["standard"])
