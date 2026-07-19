"""Transition helpers for lesson/page switches."""

from __future__ import annotations

from typing import Any


def transition_plan(*, reduce_motion: bool = False) -> dict[str, Any]:
    return {
        "lesson_enter": "none" if reduce_motion else "lxp-slide-in",
        "lesson_exit": "none" if reduce_motion else "lxp-fade",
        "panel_open": "none" if reduce_motion else "lxp-panel",
        "ai_stream": "none" if reduce_motion else "lxp-fade",
        "content_first": True,
    }
