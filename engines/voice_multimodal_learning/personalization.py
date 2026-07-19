"""Personalization — consume AIE / ALE prefs for voice presentation."""

from __future__ import annotations

from typing import Any


def personalize(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    outputs = context.get("engine_outputs") or {}
    aie = (outputs.get("accessibility") or {}).get("payload") or {}
    ale = (outputs.get("adaptive_learning") or {}).get("payload") or {}

    presentation = aie.get("presentation") or {}
    primary = presentation.get("primary_mode") or ""
    profiles = (aie.get("learner_profile") or {}).get("active_profiles") or aie.get("profiles_generated") or []

    speed = 1.0
    if "dyslexia" in profiles or primary == "auditory":
        speed = 0.75
    if "adhd" in profiles:
        speed = min(speed, 1.0)

    return {
        "voice_style": context.get("voice_style") or "Female",
        "speed": speed,
        "highlight_mode": "sentence" if "adhd" in profiles else "sentence",
        "captions": True,
        "reduced_motion": "adhd" in profiles or bool(presentation.get("reduced_motion")),
        "dyslexia_friendly": "dyslexia" in profiles,
        "focus_mode": "adhd" in profiles,
        "low_vision": "low_vision" in profiles or "blind" in profiles,
        "ale_hints": {
            "pathway": (ale.get("pathway") or {}).get("type") if isinstance(ale.get("pathway"), dict) else ale.get("pathway"),
        },
        "source_engines": ["accessibility", "adaptive_learning"],
        "presentation_only": True,
    }
