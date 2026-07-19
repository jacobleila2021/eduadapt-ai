"""VMLE usage analytics — emit structured events for LAIE."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


_EVENTS: list[dict[str, Any]] = []


def record(event_type: str, *, session_id: str = "", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {
        "ts": _now(),
        "event_type": event_type,
        "session_id": session_id,
        "payload": payload or {},
        "destination": "laie",
    }
    _EVENTS.append(row)
    if len(_EVENTS) > 2000:
        del _EVENTS[:-2000]
    return row


def summary(session_id: str = "") -> dict[str, Any]:
    rows = [e for e in _EVENTS if not session_id or e.get("session_id") == session_id]
    counts: dict[str, int] = {}
    for e in rows:
        counts[e["event_type"]] = counts.get(e["event_type"], 0) + 1
    return {
        "session_id": session_id,
        "event_counts": counts,
        "metrics": {
            "audio_usage": counts.get("audio_played", 0),
            "read_along_completion": counts.get("read_along_completed", 0),
            "voice_interactions": counts.get("voice_command", 0) + counts.get("stt", 0),
            "pronunciation_attempts": counts.get("pronunciation", 0),
            "accessibility_usage": counts.get("accessibility_applied", 0),
            "offline_learning": counts.get("offline_sync", 0),
        },
        "events": rows[-50:],
        "forward_to": "learning_analytics",
    }
