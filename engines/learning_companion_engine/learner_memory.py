"""Persistent learner companion memory — educational prefs only (no medical diagnoses)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

from engines.learning_companion_engine.schemas import LearnerCompanionMemory

MEMORY_DIR = DATA_DIR / "alcis" / "learners"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(learner_id: str) -> Path:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in learner_id)[:80]
    return MEMORY_DIR / f"{safe}.json"


def load_memory(learner_id: str) -> dict[str, Any]:
    p = _path(learner_id)
    if p.is_file():
        return json.loads(p.read_text(encoding="utf-8"))
    mem = LearnerCompanionMemory(learner_id=learner_id)
    doc = mem.to_dict()
    doc["updated_at"] = _now()
    save_memory(doc)
    return doc


def save_memory(doc: dict[str, Any]) -> dict[str, Any]:
    # Strip any accidental clinical fields
    for banned in ("diagnosis", "medical", "disorder", "disability_label"):
        doc.pop(banned, None)
    doc["updated_at"] = _now()
    _path(str(doc["learner_id"])).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc


def merge_accessibility_from_aie(doc: dict[str, Any], aie_payload: dict[str, Any] | None) -> dict[str, Any]:
    """Store functional prefs from AIE only — presentation/pacing, not diagnoses."""
    aie_payload = aie_payload or {}
    prefs = {
        "tts_preferred": bool((aie_payload.get("presentation") or {}).get("primary_mode") == "auditory"),
        "reduced_motion": bool((aie_payload.get("presentation") or {}).get("reduced_motion")),
        "profiles_functional": list(
            (aie_payload.get("learner_profile") or {}).get("active_profiles")
            or aie_payload.get("profiles_generated")
            or []
        ),
        "encouragement_frequency": "high"
        if "adhd" in str(aie_payload).lower() or "anxiety" in str((aie_payload.get("presentation") or {})).lower()
        else "medium",
    }
    # Never persist as medical diagnoses
    doc = dict(doc)
    doc["accessibility_preferences"] = prefs
    return save_memory(doc)


def update_goals(learner_id: str, goals: list[dict[str, Any]]) -> dict[str, Any]:
    doc = load_memory(learner_id)
    doc["long_term_goals"] = goals[:20]
    return save_memory(doc)


def append_reflection(learner_id: str, reflection: dict[str, Any]) -> dict[str, Any]:
    doc = load_memory(learner_id)
    hist = list(doc.get("reflection_history") or [])
    hist.append({**reflection, "ts": _now()})
    doc["reflection_history"] = hist[-50:]
    return save_memory(doc)


def record_achievement(learner_id: str, achievement: dict[str, Any]) -> dict[str, Any]:
    doc = load_memory(learner_id)
    ach = list(doc.get("achievements") or [])
    ach.append({**achievement, "ts": _now()})
    doc["achievements"] = ach[-100:]
    return save_memory(doc)
