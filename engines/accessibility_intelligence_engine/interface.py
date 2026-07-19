"""Interface adaptation — fonts, themes, focus, navigation (WCAG 2.2 AA-oriented)."""

from __future__ import annotations

from typing import Any

from engines.accessibility_intelligence_engine.schemas import InterfaceConfig, LearnerAccessibilityProfile


def build_interface_config(profile: LearnerAccessibilityProfile) -> InterfaceConfig:
    cfg = InterfaceConfig()
    profiles = set(profile.active_profiles or [])

    # Self-selected overrides first as base
    pref = profile.self_selected_preferences or {}
    if profile.preferred_font:
        cfg.font = profile.preferred_font
    if profile.preferred_colour_theme:
        cfg.colour_theme = profile.preferred_colour_theme
    if profile.preferred_line_spacing:
        cfg.line_spacing = float(profile.preferred_line_spacing)
    if profile.preferred_paragraph_spacing:
        cfg.paragraph_spacing = float(profile.preferred_paragraph_spacing)

    if "dyslexia" in profiles or "ld" in profiles:
        cfg.font = profile.preferred_font or "OpenDyslexic"
        cfg.font_size_px = max(cfg.font_size_px, 20)
        cfg.line_spacing = max(cfg.line_spacing, 1.8)
        cfg.paragraph_spacing = max(cfg.paragraph_spacing, 1.4)
        cfg.reading_ruler = True
        cfg.colour_theme = profile.preferred_colour_theme or "cream_soft"

    if "low_vision" in profiles:
        cfg.font_size_px = max(cfg.font_size_px, 24)
        cfg.contrast = "aaa"
        cfg.colour_theme = "high_contrast"
        cfg.icon_size = "large"
        cfg.touch_targets = "large"

    if "blind" in profiles:
        cfg.keyboard_navigation = True
        cfg.toolbar_layout = "screen_reader"
        cfg.animation_reduction = True

    if "adhd" in profiles or "executive_function" in profiles:
        cfg.focus_mode = True
        cfg.distraction_level = "minimal"
        cfg.animation_reduction = True
        cfg.navigation_complexity = "simplified"

    if "autism" in profiles:
        cfg.animation_reduction = True
        cfg.distraction_level = "minimal"
        cfg.colour_theme = profile.preferred_colour_theme or "calm"
        cfg.navigation_complexity = "predictable"

    if "colour_vision_deficiency" in profiles:
        cfg.colour_theme = "cvd_safe"
        cfg.contrast = "aa"

    if "motor" in profiles:
        cfg.keyboard_navigation = True
        cfg.touch_targets = "large"
        cfg.icon_size = "large"

    if "deaf" in profiles or "hard_of_hearing" in profiles:
        # visual-first chrome
        cfg.toolbar_layout = "captions_first"

    # Explicit preference overrides
    for key in (
        "font",
        "font_size_px",
        "colour_theme",
        "contrast",
        "line_spacing",
        "paragraph_spacing",
        "margins",
        "reading_ruler",
        "focus_mode",
        "animation_reduction",
        "keyboard_navigation",
        "touch_targets",
        "icon_size",
        "toolbar_layout",
        "navigation_complexity",
        "distraction_level",
    ):
        if key in pref:
            setattr(cfg, key, pref[key])

    return cfg


def interface_css_hints(cfg: InterfaceConfig) -> dict[str, Any]:
    """Hints for Streamlit/CSS consumers (accessibility.py / lesson_design)."""
    return {
        "font_family": cfg.font,
        "font_size_px": cfg.font_size_px,
        "line_height": cfg.line_spacing,
        "theme": cfg.colour_theme,
        "show_ruler": cfg.reading_ruler,
        "focus_mode": cfg.focus_mode,
        "reduce_motion": cfg.animation_reduction,
        "large_targets": cfg.touch_targets == "large",
        "wcag_contrast": cfg.contrast,
    }
