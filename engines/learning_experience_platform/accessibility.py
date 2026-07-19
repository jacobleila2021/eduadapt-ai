"""Accessibility bridge — consume AIE prefs for reader presentation."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.session_store import load_preferences, save_preferences
from engines.learning_experience_platform.themes import resolve_theme


def apply_aie(learner_id: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    aie = ((context.get("engine_outputs") or {}).get("accessibility") or {}).get("payload") or {}
    prefs = load_preferences(learner_id)
    presentation = aie.get("presentation") or {}
    hints = aie.get("interface_css_hints") or aie.get("interface") or {}

    if presentation.get("primary_mode") == "auditory":
        prefs["font_size_px"] = max(int(prefs.get("font_size_px") or 18), 22)
    profiles = (aie.get("learner_profile") or {}).get("active_profiles") or aie.get("profiles_generated") or []
    if "dyslexia" in profiles:
        prefs["font_family"] = "OpenDyslexic"
        prefs["line_spacing"] = max(float(prefs.get("line_spacing") or 1.6), 1.8)
        prefs["word_spacing"] = max(float(prefs.get("word_spacing") or 0.05), 0.12)
    if "adhd" in profiles:
        prefs["reading_mode"] = "focus"
        prefs["reading_ruler"] = True
    if "low_vision" in profiles or hints.get("theme") == "high_contrast":
        prefs["theme"] = "high_contrast"
        prefs["font_size_px"] = max(int(prefs.get("font_size_px") or 18), 24)

    prefs = save_preferences(learner_id, prefs)
    theme = resolve_theme(prefs.get("theme") or "light", hints)
    return {
        "preferences": prefs,
        "theme": theme,
        "wcag": "2.2 AA target",
        "keyboard_navigation": True,
        "screen_reader_friendly": True,
        "presentation_only": True,
        "source": "accessibility",
    }
