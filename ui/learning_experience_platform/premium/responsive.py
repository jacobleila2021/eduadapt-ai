"""Responsive layout tokens for LXP."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.phase4_schemas import BREAKPOINTS


def layout_for_width(width_px: int | None = None) -> dict[str, Any]:
    w = int(width_px or 1280)
    if w < BREAKPOINTS["mobile"]:
        device = "mobile"
        cols = [0.01, 1, 0.01]
        nav = "bottom"
    elif w < BREAKPOINTS["tablet"]:
        device = "tablet"
        cols = [0.9, 2.2, 0.01]
        nav = "collapsible"
    elif w < BREAKPOINTS["laptop"]:
        device = "laptop"
        cols = [1.0, 2.4, 1.2]
        nav = "side"
    elif w < BREAKPOINTS["whiteboard"]:
        device = "desktop"
        cols = [1.1, 2.4, 1.3]
        nav = "side"
    else:
        device = "whiteboard"
        cols = [1.2, 2.6, 1.4]
        nav = "side"
    return {
        "device": device,
        "columns": cols,
        "nav": nav,
        "touch_min_px": 44,
        "split_screen": w >= BREAKPOINTS["tablet"],
        "dynamic_type_scale": 1.0 if device != "mobile" else 0.95,
        "breakpoints": BREAKPOINTS,
    }
