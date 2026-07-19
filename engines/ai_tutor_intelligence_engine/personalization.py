"""Mode selection + personalization — teacher override respected."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import EXPLANATION_DEPTHS, TUTOR_MODES, TutorContext


def select_mode(ctx: TutorContext) -> dict[str, Any]:
    if ctx.teacher_mode_override and ctx.teacher_mode_override in TUTOR_MODES:
        return {
            "mode": ctx.teacher_mode_override,
            "reason": "Teacher override",
            "teacher_override": True,
        }
    if ctx.require_socratic or not ctx.allow_direct_answers:
        return {"mode": "socratic", "reason": "Socratic required / direct answers disabled", "teacher_override": False}

    profiles = set(ctx.accessibility_profiles or [])
    if ctx.misconceptions:
        return {"mode": "guided_discovery", "reason": "Active misconceptions — guide correction", "teacher_override": False}
    if ctx.mastery_level == "beginning" or ctx.confidence < 0.4:
        if "adhd" in profiles or "executive_function" in profiles:
            return {"mode": "step_coaching", "reason": "Low mastery + EF/attention support", "teacher_override": False}
        return {"mode": "worked_example", "reason": "Low mastery — show verified worked structure", "teacher_override": False}
    if "gifted" in profiles and ctx.mastery_level in ("proficient", "advanced"):
        return {"mode": "socratic", "reason": "Gifted + strong mastery — deepen via questioning", "teacher_override": False}
    if ctx.pathway.get("pathway_type") == "adaptive_review":
        return {"mode": "spaced_review", "reason": "ALE review pathway", "teacher_override": False}
    if ctx.pathway.get("pathway_type") == "enrichment":
        return {"mode": "guided_discovery", "reason": "Enrichment pathway", "teacher_override": False}
    return {"mode": "socratic", "reason": "Default guided tutoring", "teacher_override": False}


def select_explanation_depth(ctx: TutorContext) -> str:
    if ctx.mastery_level == "beginning" or ctx.confidence < 0.35:
        return "beginner"
    if ctx.mastery_level == "developing" or ctx.confidence < 0.55:
        return "developing"
    if "gifted" in (ctx.accessibility_profiles or []) or ctx.confidence >= 0.85:
        return "advanced"
    if ctx.mastery_level == "proficient":
        return "proficient"
    return "developing"


def personalization_rules(ctx: TutorContext) -> dict[str, Any]:
    profiles = set(ctx.accessibility_profiles or [])
    return {
        "presentation_mode": ctx.presentation_mode,
        "reading_level": ctx.reading_level,
        "simplify_vocabulary": bool(profiles.intersection({"ell", "dyslexia", "ld"})) or ctx.confidence < 0.4,
        "use_visuals_first": bool(profiles.intersection({"visual", "dyslexia", "dyscalculia"}))
        or ctx.presentation_mode in ("visual", "dyslexia"),
        "chunk_steps": bool(profiles.intersection({"adhd", "executive_function", "working_memory"})),
        "literal_language": "autism" in profiles,
        "audio_preferred": bool(profiles.intersection({"auditory", "blind", "low_vision"}))
        or ctx.presentation_mode == "auditory",
        "never_alter_academic_standards": True,
        "depth": select_explanation_depth(ctx),
        "depths_available": list(EXPLANATION_DEPTHS),
    }
