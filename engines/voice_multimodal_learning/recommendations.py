"""VMLE next-action recommendations (presentation), not curriculum invention."""

from __future__ import annotations

from typing import Any


def recommend(context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    context = context or {}
    prefs = context.get("personalization") or {}
    recs = [
        {
            "action": "start_read_along",
            "priority": 10,
            "reason": "Narrate verified lesson with highlighting",
            "engine": "voice_multimodal",
        },
        {
            "action": "ask_tutor_voice",
            "priority": 20,
            "reason": "ATIE-guided conversation with TTS",
            "engine": "ai_tutor",
        },
    ]
    if prefs.get("dyslexia_friendly"):
        recs.insert(0, {
            "action": "enable_slow_narration",
            "priority": 5,
            "reason": "AIE dyslexia profile — slower TTS",
            "engine": "accessibility",
        })
    if context.get("has_stem"):
        recs.append({
            "action": "open_interactive_stem",
            "priority": 15,
            "reason": "Explore verified STEM visuals",
            "engine": "scientific_accuracy",
        })
    return sorted(recs, key=lambda r: r["priority"])
