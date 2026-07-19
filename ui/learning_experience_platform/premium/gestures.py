"""Touch & gesture contracts + keyboard equivalents."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.phase4_schemas import GESTURES


def gesture_map() -> dict[str, Any]:
    return {
        "swipe_nav": {"action": "next_prev_lesson", "keyboard": "j/k"},
        "pinch_zoom": {"action": "diagram_zoom", "keyboard": "+/-"},
        "long_press": {"action": "context_menu", "keyboard": "Shift+F10"},
        "drag_drop_notes": {"action": "reposition_note", "keyboard": "Alt+Arrow"},
        "touch_highlight": {"action": "highlight_selection", "keyboard": "h"},
        "gesture_bookmark": {"action": "bookmark_here", "keyboard": "b"},
        "double_tap_zoom": {"action": "zoom_reset", "keyboard": "0"},
        "haptic": {"action": "optional_feedback", "keyboard": None},
        "supported": list(GESTURES),
        "keyboard_equivalents": True,
    }
