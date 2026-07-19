"""LMAS analytics → LAIE-shaped events."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


_EVENTS: list[dict[str, Any]] = []


def record(event_type: str, *, learner_id: str = "", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {"ts": _now(), "event_type": event_type, "learner_id": learner_id, "payload": payload or {}, "destination": "laie"}
    _EVENTS.append(row)
    if len(_EVENTS) > 3000:
        del _EVENTS[:-3000]
    return row


def summary(learner_id: str = "", state: dict[str, Any] | None = None) -> dict[str, Any]:
    state = state or {}
    rows = [e for e in _EVENTS if not learner_id or e.get("learner_id") == learner_id]
    counts: dict[str, int] = {}
    for e in rows:
        counts[e["event_type"]] = counts.get(e["event_type"], 0) + 1
    return {
        "learner_id": learner_id,
        "xp_total": state.get("xp_total"),
        "event_counts": counts,
        "metrics": {
            "xp_growth": state.get("xp_total") or 0,
            "achievement_rates": len(state.get("achievements") or []),
            "quest_completion": len([q for q in (state.get("quests") or []) if q.get("status") == "completed"]),
            "streak_health": (state.get("streaks") or {}).get("daily"),
            "certificates": len(state.get("certificates") or []),
        },
        "events": rows[-40:],
        "forward_to": "learning_analytics",
    }
