"""Accessibility Intelligence — main facade for VLIE AccessibilityEngine."""

from __future__ import annotations

from typing import Any

from engines.accessibility_intelligence_engine.accommodations import apply_accommodations
from engines.accessibility_intelligence_engine.assistive import recommend_assistive_tech
from engines.accessibility_intelligence_engine.indexing import rebuild_aie_index
from engines.accessibility_intelligence_engine.interface import build_interface_config, interface_css_hints
from engines.accessibility_intelligence_engine.language_support import (
    executive_function_supports,
    language_supports,
)
from engines.accessibility_intelligence_engine.learner_profile import (
    build_profile_from_context,
    save_profile,
)
from engines.accessibility_intelligence_engine.presentation import (
    presentation_presets_for_mode,
    select_presentation_mode,
)
from engines.accessibility_intelligence_engine.readability import readability_report
from engines.accessibility_intelligence_engine.schemas import SUPPORTED_PROFILES, WCAG_TARGET, UDL_VERSION
from engines.accessibility_intelligence_engine.sensory_profiles import catalog


def _cie_hints(context: dict[str, Any]) -> dict[str, Any]:
    curr = (context.get("engine_outputs") or {}).get("curriculum") or {}
    payload = curr.get("payload") if isinstance(curr, dict) else {}
    if not isinstance(payload, dict):
        return {}
    cie = payload.get("curriculum_intelligence") or {}
    return cie.get("adaptations") or {}


def _adaptation_specs_catalog() -> tuple[list[str], list[str]]:
    try:
        from adaptation_specs import ADAPTATION_SPECS, OUTPUT_KEYS

        enabled = [s["id"] for s in ADAPTATION_SPECS if s.get("generate")]
        return enabled, list(OUTPUT_KEYS)
    except Exception:  # noqa: BLE001
        return [], []


def analyze_accessibility_context(context: dict[str, Any]) -> dict[str, Any]:
    """
    Full AIE package for VLIE.
    Presentation personalization only — curriculum/STEM/official answers locked.
    """
    profile = build_profile_from_context(context)
    # Persist when real learner
    if profile.learner_id and profile.learner_id != "anonymous":
        try:
            save_profile(profile)
        except Exception:  # noqa: BLE001
            pass

    cie_hints = _cie_hints(context)
    package = apply_accommodations(profile, cie_adaptations=cie_hints)
    presentation = select_presentation_mode(profile)
    mode = presentation.get("primary_mode") or "standard"
    presets = {
        mode: presentation_presets_for_mode(mode),
        "dyslexia": presentation_presets_for_mode("dyslexia"),
        "adhd": presentation_presets_for_mode("adhd"),
        "autism": presentation_presets_for_mode("autism"),
        "ell": presentation_presets_for_mode("ell"),
        "dyscalculia": presentation_presets_for_mode("dyscalculia"),
    }
    # Merge primary into presets map used by AdaptiveLearningEngine historically
    presets.update({presentation.get("adaptation_spec_id") or mode: presentation_presets_for_mode(mode)})

    interface = build_interface_config(profile)
    lesson = context.get("lesson_text") or ""
    readability = readability_report(lesson) if lesson else {}
    vocab = []
    if isinstance(context.get("vocabulary_terms"), list):
        vocab = context["vocabulary_terms"]

    generated_specs, output_keys = _adaptation_specs_catalog()
    prioritized = package.get("prioritized_adaptation_specs") or []
    # profiles_generated: intersection of catalog generate flags and learner needs (+ always include prioritized)
    profiles_generated = []
    for sid in prioritized:
        if sid in generated_specs or sid in ("standard", "executive", "parent_summary"):
            profiles_generated.append(sid)
    for sid in generated_specs:
        if sid in prioritized and sid not in profiles_generated:
            profiles_generated.append(sid)
    if not profiles_generated:
        profiles_generated = prioritized or ["standard"]

    tutor_brief = {
        "adjust_language": "ell" in profile.active_profiles or "dyslexia" in profile.active_profiles,
        "adjust_pacing": "adhd" in profile.active_profiles or "processing_speed" in profile.active_profiles,
        "adjust_explanation_depth": "gifted" in profile.active_profiles,
        "adjust_interaction_style": "autism" in profile.active_profiles,
        "adjust_encouragement": True,
        "never_alter_curriculum_accuracy": True,
        "active_profiles": list(profile.active_profiles),
        "interface_hints": interface_css_hints(interface),
    }

    return {
        # Backward-compatible AccessibilityEngine keys
        "profiles_available": list(SUPPORTED_PROFILES),
        "profiles_generated": profiles_generated,
        "output_keys": output_keys,
        "presets": presets,
        "wcag_target": WCAG_TARGET,
        "facts_immutable": True,
        # AIE enrichment
        "udl": UDL_VERSION,
        "learner_profile": profile.to_dict(),
        "presentation": presentation,
        "interface": interface.to_dict(),
        "interface_css_hints": interface_css_hints(interface),
        "accommodations": package,
        "assistive_technology": recommend_assistive_tech(profile),
        "language_support": language_supports(profile, vocabulary=vocab),
        "executive_function_supports": executive_function_supports(profile),
        "readability": readability,
        "tutor_brief": tutor_brief,
        "profile_catalog": {k: v.get("label") for k, v in catalog().items()},
        "policy": package["policy"],
        "aie_version": "1.0.0",
    }


def ensure_indexed() -> dict[str, Any]:
    return rebuild_aie_index()
