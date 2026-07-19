"""Reader themes & CSS tokens — presentation only."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.schemas import THEMES

THEME_TOKENS: dict[str, dict[str, str]] = {
    "light": {
        "bg": "#FAFAF8",
        "fg": "#1A1A1A",
        "panel": "#FFFFFF",
        "accent": "#2F6F5E",
        "muted": "#6B6B6B",
    },
    "dark": {
        "bg": "#12141A",
        "fg": "#E8E8E8",
        "panel": "#1C1F28",
        "accent": "#7BC4A8",
        "muted": "#9AA0A6",
    },
    "sepia": {
        "bg": "#F4ECD8",
        "fg": "#3B2F2F",
        "panel": "#FBF6EA",
        "accent": "#8B5E3C",
        "muted": "#7A6A55",
    },
    "high_contrast": {
        "bg": "#000000",
        "fg": "#FFFFFF",
        "panel": "#000000",
        "accent": "#FFFF00",
        "muted": "#FFFFFF",
    },
}


def resolve_theme(name: str, aie_hints: dict[str, Any] | None = None) -> dict[str, Any]:
    aie_hints = aie_hints or {}
    theme = name if name in THEMES else "light"
    # AIE may recommend high contrast / calm
    recommended = (aie_hints.get("theme") or aie_hints.get("preferred_theme") or "").lower()
    if recommended in ("high_contrast", "high-contrast"):
        theme = "high_contrast"
    tokens = THEME_TOKENS[theme]
    return {
        "theme": theme,
        "tokens": tokens,
        "css_variables": {f"--lxp-{k}": v for k, v in tokens.items()},
        "themes_available": list(THEMES),
        "source_aie": bool(aie_hints),
    }


def reading_mode_css(mode: str) -> dict[str, Any]:
    return {
        "mode": mode,
        "focus_distraction_free": mode in ("focus", "fullscreen"),
        "paged": mode == "paged",
        "continuous": mode == "continuous_scroll",
        "fullscreen": mode == "fullscreen",
    }
