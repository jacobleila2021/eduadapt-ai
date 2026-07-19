"""Personalization from AIE — reward frequency & celebration intensity."""

from __future__ import annotations

from typing import Any


def personalize(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    aie = ((context.get("engine_outputs") or {}).get("accessibility") or {}).get("payload") or {}
    profiles = (aie.get("learner_profile") or {}).get("active_profiles") or aie.get("profiles_generated") or []
    presentation = aie.get("presentation") or {}

    intensity = "standard"
    reward_frequency = "medium"
    visual_complexity = "standard"
    if "adhd" in profiles:
        reward_frequency = "high"
        intensity = "calm_frequent"  # more check-ins, softer celebrations
        visual_complexity = "reduced"
    if "anxiety" in str(profiles).lower() or presentation.get("reduced_motion"):
        intensity = "gentle"
        visual_complexity = "reduced"
    if "dyslexia" in profiles:
        visual_complexity = "reduced"

    return {
        "notification_style": "gentle" if intensity == "gentle" else "standard",
        "visual_complexity": visual_complexity,
        "reward_frequency": reward_frequency,
        "interaction_style": "supportive",
        "celebration_intensity": intensity,
        "source": "accessibility",
        "presentation_only": True,
    }
