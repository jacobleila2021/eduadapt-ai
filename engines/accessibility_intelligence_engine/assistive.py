"""Assistive technology compatibility recommendations."""

from __future__ import annotations

from typing import Any

from engines.accessibility_intelligence_engine.schemas import LearnerAccessibilityProfile

AT_CATALOG = {
    "screen_reader": {
        "name": "Screen reader",
        "when": ["blind", "low_vision"],
        "requirements": ["semantic_headings", "alt_text", "aria_labels", "skip_links"],
    },
    "text_to_speech": {
        "name": "Text-to-Speech",
        "when": ["dyslexia", "blind", "low_vision", "auditory", "adhd", "ell"],
        "requirements": ["clean_passage_text", "speed_control", "transcript"],
        "integrates": "audio_learning.py",
    },
    "speech_to_text": {
        "name": "Speech-to-Text",
        "when": ["dysgraphia", "motor"],
        "requirements": ["oral_response_fields"],
    },
    "braille_display": {
        "name": "Braille display",
        "when": ["blind"],
        "requirements": ["text_alternatives", "linear_reading_order"],
        "status": "future_ready",
    },
    "keyboard_only": {
        "name": "Keyboard-only navigation",
        "when": ["motor", "blind"],
        "requirements": ["focus_visible", "no_keyboard_trap"],
    },
    "switch_access": {
        "name": "Switch access",
        "when": ["motor"],
        "requirements": ["sequential_focus", "large_targets"],
        "status": "future_ready",
    },
    "eye_tracking": {
        "name": "Eye tracking",
        "when": ["motor"],
        "requirements": ["dwell_compatible_targets"],
        "status": "future_ready",
    },
    "captioning": {
        "name": "Captioning",
        "when": ["deaf", "hard_of_hearing"],
        "requirements": ["synced_captions", "transcripts"],
    },
    "transcripts": {
        "name": "Transcripts",
        "when": ["deaf", "hard_of_hearing", "auditory", "ell"],
        "requirements": ["full_transcript_panel"],
        "integrates": "audio_learning.py",
    },
}


def recommend_assistive_tech(profile: LearnerAccessibilityProfile) -> list[dict[str, Any]]:
    profiles = set(profile.active_profiles or [])
    out = []
    for at_id, meta in AT_CATALOG.items():
        if profiles.intersection(meta.get("when") or []):
            out.append(
                {
                    "at_id": at_id,
                    "name": meta["name"],
                    "requirements": meta.get("requirements") or [],
                    "integrates": meta.get("integrates"),
                    "status": meta.get("status") or "supported",
                    "compatibility": "recommended",
                }
            )
    # Always recommend keyboard as baseline WCAG
    if not any(r["at_id"] == "keyboard_only" for r in out):
        out.append(
            {
                "at_id": "keyboard_only",
                "name": "Keyboard-only navigation",
                "requirements": ["focus_visible"],
                "status": "baseline_wcag",
                "compatibility": "always_on",
            }
        )
    return out
