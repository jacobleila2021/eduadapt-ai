"""Session memory — JSON-backed; privacy-aware retention."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

SESSIONS_DIR = DATA_DIR / "atie" / "sessions"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(session_id: str) -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)[:80]
    return SESSIONS_DIR / f"{safe}.json"


def start_session(learner_id: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    sid = f"tut_{uuid.uuid4().hex[:12]}"
    doc = {
        "session_id": sid,
        "learner_id": learner_id,
        "started_at": _now(),
        "ended_at": None,
        "meta": meta or {},
        "turns": [],
        "concepts_discussed": [],
        "hints_used": [],
        "misconceptions_addressed": [],
        "reflections": [],
        "goals": [],
        "progress": {},
        "retention_policy": "configurable_local_json_no_medical_data",
    }
    _path(sid).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc


def load_session(session_id: str) -> dict[str, Any] | None:
    path = _path(session_id)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_session(doc: dict[str, Any]) -> Path:
    path = _path(doc["session_id"])
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def append_turn(session_id: str, turn: dict[str, Any]) -> dict[str, Any]:
    doc = load_session(session_id) or start_session("unknown", {"recovered": True})
    if doc.get("session_id") != session_id and session_id:
        # if recovered wrong id, keep provided
        pass
    doc = load_session(session_id)
    if not doc:
        raise FileNotFoundError(session_id)
    doc.setdefault("turns", []).append({**turn, "at": _now()})
    if turn.get("concept_id"):
        doc.setdefault("concepts_discussed", [])
        if turn["concept_id"] not in doc["concepts_discussed"]:
            doc["concepts_discussed"].append(turn["concept_id"])
    if turn.get("hint_level") is not None:
        doc.setdefault("hints_used", []).append(turn.get("hint_level"))
    save_session(doc)
    return doc


def end_session(session_id: str, progress: dict[str, Any] | None = None) -> dict[str, Any]:
    doc = load_session(session_id)
    if not doc:
        raise FileNotFoundError(session_id)
    doc["ended_at"] = _now()
    if progress:
        doc["progress"] = progress
    save_session(doc)
    return doc


def record_reflection(session_id: str, reflection: dict[str, Any]) -> dict[str, Any]:
    doc = load_session(session_id)
    if not doc:
        raise FileNotFoundError(session_id)
    doc.setdefault("reflections", []).append({**reflection, "at": _now()})
    save_session(doc)
    return doc
