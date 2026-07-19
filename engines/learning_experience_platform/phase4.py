"""Phase 4 aggregator — premium experience plan (no new intelligence engines)."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.phase4_analytics import experience_summary, track_experience
from engines.learning_experience_platform.phase4_offline import sync_status, storage_optimization_report
from engines.learning_experience_platform.phase4_schemas import (
    ANIMATION_PRESETS,
    BREAKPOINTS,
    CURRICULUM_TRANSLATION_POLICY,
    GESTURES,
    SUPPORTED_UI_LOCALES,
)
from engines.learning_experience_platform.phase4_settings import load_premium_settings, notification_preferences


def build_phase4(context: dict[str, Any]) -> dict[str, Any]:
    learner_id = str(context.get("learner_id") or context.get("user_id") or "anonymous")
    settings = load_premium_settings(learner_id)
    reduce_motion = bool(settings.get("reduce_motion") or context.get("reduce_motion"))

    track_experience(
        "session_plan",
        learner_id=learner_id,
        payload={
            "device": context.get("device_type") or "unknown",
            "screen": context.get("screen_size") or "unknown",
            "reduce_motion": reduce_motion,
            "locale": settings.get("language"),
        },
    )

    return {
        "system": "LXP",
        "phase": "phase4_premium_experience",
        "settings": settings,
        "motion": {
            "presets": list(ANIMATION_PRESETS),
            "enabled": not reduce_motion,
            "reduce_motion": reduce_motion,
            "never_delay_content": True,
            "duration_ms": 0 if reduce_motion else 180,
        },
        "performance": {
            "lazy_loading": True,
            "virtual_scrolling": True,
            "memoization": True,
            "image_optimization": True,
            "diagram_caching": True,
            "formula_caching": True,
            "progressive_rendering": True,
            "background_prefetch": True,
            "targets": {
                "smooth_scroll_fps": 60,
                "fast_initial_render": True,
                "low_memory": True,
            },
        },
        "offline": {
            **sync_status(learner_id),
            "storage": storage_optimization_report(learner_id),
            "full_packages": True,
            "delta_sync": True,
            "conflict_resolution": True,
            "background_sync": True,
        },
        "pwa": {
            "installable": True,
            "offline_shell": True,
            "service_worker": True,
            "manifest": "/static/lxp/manifest.webmanifest",
            "splash": True,
            "push_optional": True,
            "graceful_fallback": True,
        },
        "responsive": {
            "breakpoints": BREAKPOINTS,
            "adaptive_nav": True,
            "split_screen": True,
            "touch_friendly": True,
            "dynamic_typography": True,
        },
        "gestures": {
            "supported": list(GESTURES),
            "keyboard_equivalents": True,
            "haptic_when_available": True,
        },
        "multilingual": {
            "ui_locales": list(SUPPORTED_UI_LOCALES),
            "active": settings.get("language") or "en",
            "rtl_ready": bool(settings.get("rtl_ready", True)),
            "curriculum_policy": CURRICULUM_TRANSLATION_POLICY,
            "vmle_narration": True,
            "dual_language_glossary": True,
            "unicode": True,
        },
        "accessibility": {
            "wcag": "2.2 AA",
            "reduce_motion": reduce_motion,
            "enhanced_focus": True,
            "high_contrast": bool(settings.get("high_contrast")),
            "keyboard_shortcuts_overlay": True,
            "larger_touch_targets": True,
            "aria_labels": True,
            "source": "AIE",
        },
        "loading": {
            "skeletons": True,
            "progressive": True,
            "diagram_placeholders": True,
            "ai_indicators": True,
            "offline_states": True,
            "retry": True,
        },
        "notifications": notification_preferences(learner_id),
        "analytics": experience_summary(learner_id),
        "policy": {
            "no_new_intelligence_engines": True,
            "consume_existing_outputs_only": True,
            "never_auto_translate_curriculum": True,
            "never_delay_learning_content": True,
        },
    }
