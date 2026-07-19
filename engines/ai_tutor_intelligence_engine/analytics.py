"""Tutor analytics — feeds LAIE."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

ANALYTICS_DIR = DATA_DIR / "atie" / "analytics"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(learner_id: str) -> Path:
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in learner_id)[:80]
    return ANALYTICS_DIR / f"{safe}.json"


def load_analytics(learner_id: str) -> dict[str, Any]:
    path = _path(learner_id)
    if not path.is_file():
        return {
            "learner_id": learner_id,
            "sessions": 0,
            "questions_asked": 0,
            "hints_requested": 0,
            "misconceptions_corrected": 0,
            "events": [],
            "totals": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def record_tutor_event(learner_id: str, event_type: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    state = load_analytics(learner_id)
    state.setdefault("events", []).append({"at": _now(), "type": event_type, "meta": meta or {}})
    state["events"] = state["events"][-200:]
    if event_type == "session_start":
        state["sessions"] = int(state.get("sessions") or 0) + 1
    elif event_type == "question":
        state["questions_asked"] = int(state.get("questions_asked") or 0) + 1
    elif event_type == "hint":
        state["hints_requested"] = int(state.get("hints_requested") or 0) + 1
    elif event_type == "misconception_corrected":
        state["misconceptions_corrected"] = int(state.get("misconceptions_corrected") or 0) + 1
    _path(learner_id).write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state


def tutor_analytics_summary(learner_id: str) -> dict[str, Any]:
    state = load_analytics(learner_id)
    return {
        "learner_id": learner_id,
        "session_count": state.get("sessions") or 0,
        "questions_asked": state.get("questions_asked") or 0,
        "hints_requested": state.get("hints_requested") or 0,
        "misconceptions_corrected": state.get("misconceptions_corrected") or 0,
        "recent_events": (state.get("events") or [])[-10:],
        "feeds_laie": True,
    }
