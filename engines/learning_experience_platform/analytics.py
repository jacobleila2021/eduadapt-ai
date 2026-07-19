"""LXP analytics → LAIE events."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from engines.learning_experience_platform.progress import laie_reader_payload


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


_EVENTS: list[dict[str, Any]] = []


def track(event_type: str, *, learner_id: str = "", lesson_id: str = "", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {
        "ts": _now(),
        "event_type": event_type,
        "learner_id": learner_id,
        "lesson_id": lesson_id,
        "payload": payload or {},
        "destination": "laie",
    }
    _EVENTS.append(row)
    if len(_EVENTS) > 4000:
        del _EVENTS[:-4000]
    return row


def summary(learner_id: str = "", lesson_id: str = "") -> dict[str, Any]:
    rows = [
        e
        for e in _EVENTS
        if (not learner_id or e.get("learner_id") == learner_id)
        and (not lesson_id or e.get("lesson_id") == lesson_id)
    ]
    counts: dict[str, int] = {}
    for e in rows:
        counts[e["event_type"]] = counts.get(e["event_type"], 0) + 1
    reader = laie_reader_payload(learner_id, lesson_id) if learner_id and lesson_id else {}
    return {
        "event_counts": counts,
        "metrics": {
            "reading_time_events": counts.get("reading_time", 0),
            "glossary_usage": counts.get("glossary", 0),
            "ai_help": counts.get("ai_explain", 0) + counts.get("chat", 0),
            "read_along": counts.get("read_along", 0),
            "stem": counts.get("stem", 0),
            "bookmarks": counts.get("bookmark", 0),
            "highlights": counts.get("highlight", 0),
            "notes": counts.get("note", 0),
            "offline": counts.get("offline", 0),
            "accessibility": counts.get("accessibility", 0),
        },
        "lesson_reader": reader,
        "events": rows[-40:],
        "forward_to": "learning_analytics",
    }
