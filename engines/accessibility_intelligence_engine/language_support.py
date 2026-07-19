"""Language support scaffolds — presentation only (no fact changes)."""

from __future__ import annotations

from typing import Any

from engines.accessibility_intelligence_engine.schemas import LearnerAccessibilityProfile


def language_supports(profile: LearnerAccessibilityProfile, *, vocabulary: list[str] | None = None) -> dict[str, Any]:
    profiles = set(profile.active_profiles or [])
    needs_lang = bool(profiles.intersection({"ell", "dyslexia", "ld", "deaf", "hard_of_hearing", "auditory"}))
    vocab = list(vocabulary or [])[:20]

    return {
        "enabled": needs_lang or bool(profile.language_proficiency),
        "vocabulary_scaffolds": needs_lang,
        "definitions": needs_lang,
        "pronunciation_hints": "ell" in profiles or "dyslexia" in profiles,
        "dual_language_glossaries": "ell" in profiles,
        "translation_layer": "ell" in profiles,  # placeholder hook
        "simplified_language_presentation": "ell" in profiles or "ld" in profiles,
        "academic_vocabulary_highlighting": True if vocab or needs_lang else False,
        "sentence_chunking": "ell" in profiles or "dyslexia" in profiles or "adhd" in profiles,
        "sample_terms": vocab,
        "language_proficiency": profile.language_proficiency or "",
        "policy": "scaffolds_only_curriculum_locked",
    }


def executive_function_supports(profile: LearnerAccessibilityProfile) -> dict[str, Any]:
    profiles = set(profile.active_profiles or [])
    need = bool(
        profiles.intersection(
            {"adhd", "executive_function", "working_memory", "processing_speed", "autism", "twice_exceptional"}
        )
    )
    return {
        "enabled": need,
        "task_chunking": need,
        "step_by_step_instructions": need,
        "visual_schedules": "autism" in profiles or "adhd" in profiles,
        "timers": "adhd" in profiles or "executive_function" in profiles,
        "checklists": need,
        "progress_trackers": need,
        "planning_templates": "executive_function" in profiles or "working_memory" in profiles,
        "goal_reminders": need,
        "reflection_prompts": need,
        "policy": "ef_scaffolds_presentation_only",
    }
