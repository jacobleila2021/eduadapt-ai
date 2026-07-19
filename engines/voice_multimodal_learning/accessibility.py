"""Accessibility presentation for VMLE — consumes AIE; never changes facts."""

from __future__ import annotations

from typing import Any

from engines.voice_multimodal_learning.personalization import personalize


def apply_aie(context: dict[str, Any] | None = None) -> dict[str, Any]:
    prefs = personalize(context)
    return {
        "dyslexia_friendly_reading": prefs.get("dyslexia_friendly"),
        "adhd_focus_mode": prefs.get("focus_mode"),
        "low_vision_mode": prefs.get("low_vision"),
        "screen_reader": True,
        "captions": prefs.get("captions", True),
        "keyboard_navigation": True,
        "switch_access": True,
        "reduced_motion": prefs.get("reduced_motion"),
        "adjustable_contrast": True,
        "tts_speed": prefs.get("speed"),
        "policy": "accessibility_overrides_presentation_only",
        "source": "accessibility_intelligence_engine",
    }
