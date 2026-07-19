"""Accessibility-aware companion presentation — consumes AIE only."""

from __future__ import annotations

from typing import Any


def companion_a11y(context: dict[str, Any] | None = None, memory: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    memory = memory or {}
    outputs = context.get("engine_outputs") or {}
    aie = (outputs.get("accessibility") or {}).get("payload") or {}
    prefs = memory.get("accessibility_preferences") or {}
    profiles = prefs.get("profiles_functional") or (aie.get("learner_profile") or {}).get("active_profiles") or []

    tone = "gentle"
    pace = "slow" if "dyslexia" in profiles or prefs.get("tts_preferred") else "steady"
    freq = prefs.get("encouragement_frequency") or ("high" if "adhd" in profiles else "medium")
    return {
        "tone": tone,
        "pace": pace,
        "encouragement_frequency": freq,
        "visual_complexity": "reduced" if "adhd" in profiles or "low_vision" in profiles else "standard",
        "reading_level": "simplified_companion_copy" if "ell" in profiles or "dyslexia" in profiles else "standard",
        "audio_usage": bool(prefs.get("tts_preferred") or (aie.get("presentation") or {}).get("primary_mode") == "auditory"),
        "reminder_frequency": freq,
        "source": "accessibility_intelligence_engine",
        "presentation_only": True,
        "no_medical_storage": True,
    }
