"""ALE analytics — pathway and intervention effectiveness signals."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

ANALYTICS_DIR = DATA_DIR / "ale" / "analytics"


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
            "totals": {
                "pathway_changes": 0,
                "interventions_assigned": 0,
                "enrichment_offered": 0,
                "reviews_completed": 0,
            },
        }
    return json.loads(path.read_text(encoding="utf-8"))


def record_event(learner_id: str, event_type: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    state = load_analytics(learner_id)
    state["events"].append({"at": _now(), "type": event_type, "meta": meta or {}})
    state["events"] = state["events"][-300:]
    totals = state.setdefault("totals", {})
    key_map = {
        "pathway_change": "pathway_changes",
        "intervention": "interventions_assigned",
        "enrichment": "enrichment_offered",
        "review_complete": "reviews_completed",
    }
    if event_type in key_map:
        k = key_map[event_type]
        totals[k] = int(totals.get(k) or 0) + 1
    _path(learner_id).write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    return state


def analytics_summary(learner_id: str, model_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    state = load_analytics(learner_id)
    snap = model_snapshot or {}
    return {
        "learner_id": learner_id,
        "totals": state.get("totals") or {},
        "mastery_snapshot": {
            "mastered": len(snap.get("concepts_mastered") or []),
            "developing": len(snap.get("concepts_developing") or []),
            "at_risk": len(snap.get("concepts_at_risk") or []),
            "confidence": snap.get("confidence"),
        },
        "recent_events": (state.get("events") or [])[-10:],
        "metrics_tracked": [
            "mastery_growth",
            "learning_velocity",
            "review_effectiveness",
            "intervention_success",
            "enrichment_uptake",
            "confidence_trends",
            "time_to_mastery",
            "knowledge_retention",
            "adaptive_pathway_changes",
        ],
    }
