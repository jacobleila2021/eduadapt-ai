"""Read-along synchronization — pause/resume, bookmarks, section jumps."""

from __future__ import annotations

from typing import Any

from engines.voice_multimodal_learning.highlighting import build_highlight_timeline
from engines.voice_multimodal_learning.schemas import NarrationPlan


def create_read_along_state(
    plan: NarrationPlan | dict[str, Any],
    *,
    highlight_mode: str = "sentence",
    speed: float = 1.0,
) -> dict[str, Any]:
    if isinstance(plan, NarrationPlan):
        plan_d = plan.to_dict()
    else:
        plan_d = dict(plan)
    timeline = build_highlight_timeline(
        plan_d.get("sentences") or [],
        plan_d.get("paragraphs") or [],
        plan_d.get("text") or "",
        mode=highlight_mode,
        speed=speed or float(plan_d.get("speed") or 1.0),
    )
    return {
        "status": "ready",
        "playing": False,
        "paused": False,
        "index": 0,
        "highlight_mode": highlight_mode,
        "speed": speed,
        "timeline": timeline,
        "bookmark": None,
        "total_units": len(timeline),
    }


def pause(state: dict[str, Any]) -> dict[str, Any]:
    state = dict(state)
    state["playing"] = False
    state["paused"] = True
    state["status"] = "paused"
    return state


def resume(state: dict[str, Any]) -> dict[str, Any]:
    state = dict(state)
    state["playing"] = True
    state["paused"] = False
    state["status"] = "playing"
    return state


def set_speed(state: dict[str, Any], speed: float) -> dict[str, Any]:
    from engines.voice_multimodal_learning.schemas import PLAYBACK_SPEEDS

    state = dict(state)
    # snap to nearest supported
    speed = min(PLAYBACK_SPEEDS, key=lambda s: abs(s - float(speed)))
    state["speed"] = speed
    return state


def repeat_unit(state: dict[str, Any], *, unit: str = "sentence") -> dict[str, Any]:
    state = dict(state)
    state["action"] = f"repeat_{unit}"
    state["playing"] = True
    return state


def jump_to(state: dict[str, Any], index: int) -> dict[str, Any]:
    state = dict(state)
    total = int(state.get("total_units") or 0)
    state["index"] = max(0, min(index, max(total - 1, 0)))
    state["action"] = "jump"
    return state


def bookmark(state: dict[str, Any], label: str = "") -> dict[str, Any]:
    state = dict(state)
    state["bookmark"] = {"index": state.get("index", 0), "label": label or "bookmark"}
    return state
