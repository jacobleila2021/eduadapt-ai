"""Accessibility analytics — functional support usage (no medical data)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

ANALYTICS_DIR = DATA_DIR / "aie" / "analytics"


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
            "events": [],
            "preferred_supports": {},
            "totals": {
                "completion_signals": 0,
                "audio_usage": 0,
                "focus_mode_usage": 0,
                "ruler_usage": 0,
                "accommodation_usage": 0,
            },
        }
    return json.loads(path.read_text(encoding="utf-8"))


def record_event(learner_id: str, event_type: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    state = load_analytics(learner_id)
    state["events"].append({"at": _now(), "type": event_type, "meta": meta or {}})
    state["events"] = state["events"][-200:]
    totals = state.setdefault("totals", {})
    if event_type == "audio_play":
        totals["audio_usage"] = int(totals.get("audio_usage") or 0) + 1
    elif event_type == "focus_mode":
        totals["focus_mode_usage"] = int(totals.get("focus_mode_usage") or 0) + 1
    elif event_type == "ruler":
        totals["ruler_usage"] = int(totals.get("ruler_usage") or 0) + 1
    elif event_type == "accommodation_applied":
        totals["accommodation_usage"] = int(totals.get("accommodation_usage") or 0) + 1
    elif event_type == "lesson_complete":
        totals["completion_signals"] = int(totals.get("completion_signals") or 0) + 1
    support = (meta or {}).get("support_id")
    if support:
        prefs = state.setdefault("preferred_supports", {})
        prefs[support] = int(prefs.get(support) or 0) + 1
    path = _path(learner_id)
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state


def analytics_summary(learner_id: str) -> dict[str, Any]:
    state = load_analytics(learner_id)
    prefs = state.get("preferred_supports") or {}
    top = sorted(prefs.items(), key=lambda kv: -kv[1])[:8]
    return {
        "learner_id": learner_id,
        "totals": state.get("totals") or {},
        "preferred_supports": [{"support_id": k, "count": v} for k, v in top],
        "recent_events": (state.get("events") or [])[-10:],
        "policy": "functional_preferences_only_no_medical_diagnoses",
    }
