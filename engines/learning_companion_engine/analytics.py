"""ALCIS analytics — forward structured events to LAIE."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


_EVENTS: list[dict[str, Any]] = []


def record(event_type: str, *, learner_id: str = "", session_id: str = "", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {
        "ts": _now(),
        "event_type": event_type,
        "learner_id": learner_id,
        "session_id": session_id,
        "payload": payload or {},
        "destination": "laie",
    }
    _EVENTS.append(row)
    if len(_EVENTS) > 3000:
        del _EVENTS[:-3000]
    return row


def summary(learner_id: str = "") -> dict[str, Any]:
    rows = [e for e in _EVENTS if not learner_id or e.get("learner_id") == learner_id]
    counts: dict[str, int] = {}
    for e in rows:
        counts[e["event_type"]] = counts.get(e["event_type"], 0) + 1
    return {
        "learner_id": learner_id,
        "event_counts": counts,
        "metrics": {
            "companion_interactions": counts.get("dialogue", 0) + counts.get("encouragement", 0),
            "celebrations": counts.get("celebration", 0),
            "ef_coaching": counts.get("ef_coach", 0),
            "wellbeing_supports": counts.get("wellbeing", 0),
            "goal_updates": counts.get("goal_update", 0),
            "reflections": counts.get("reflection", 0),
        },
        "events": rows[-40:],
        "forward_to": "learning_analytics",
        "dashboards": {
            "learner": ["choose_companion", "achievements", "goals", "memories"],
            "teacher": ["usage", "motivation_trends", "engagement", "classroom_settings"],
            "parent": ["motivation_progress", "habits", "achievements", "daily_summary"],
        },
    }
