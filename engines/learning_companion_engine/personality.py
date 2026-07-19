"""Personality styles — interaction tone only; no academic content generation."""

from __future__ import annotations

from typing import Any

from engines.learning_companion_engine.avatars import validate_style
from engines.learning_companion_engine.schemas import PERSONALITY_STYLES

_STYLE_PROMPTS = {
    "gentle_coach": {"tone": "warm", "energy": "low", "prefix": ""},
    "cheerful_friend": {"tone": "upbeat", "energy": "high", "prefix": ""},
    "curious_explorer": {"tone": "wonder", "energy": "medium", "prefix": ""},
    "calm_mentor": {"tone": "steady", "energy": "low", "prefix": ""},
    "energetic_motivator": {"tone": "bold", "energy": "high", "prefix": ""},
    "professional_mentor": {"tone": "respectful", "energy": "medium", "prefix": ""},
}


def apply_style(text: str, style: str) -> dict[str, Any]:
    style = validate_style(style)
    meta = _STYLE_PROMPTS[style]
    # Soft wrappers — do not invent facts
    wrappers = {
        "gentle_coach": "I'm proud of how you're working. {t}",
        "cheerful_friend": "You've got this! {t}",
        "curious_explorer": "Interesting progress — {t}",
        "calm_mentor": "{t}",
        "energetic_motivator": "Yes! {t}",
        "professional_mentor": "Noted. {t}",
    }
    rendered = wrappers[style].format(t=text)
    return {"style": style, "text": rendered, "meta": meta, "styles_available": list(PERSONALITY_STYLES)}


def update_personality(memory: dict[str, Any], style: str) -> dict[str, Any]:
    memory = dict(memory)
    memory["communication_style"] = validate_style(style)
    return memory
