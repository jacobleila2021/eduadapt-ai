"""ALCIS session memory — short-lived companion session state."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from knowledge.paths import DATA_DIR

SESSIONS_DIR = DATA_DIR / "alcis" / "sessions"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(session_id: str) -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)[:80]
    return SESSIONS_DIR / f"{safe}.json"


def start_session(learner_id: str, *, companion_id: str = "study_panda", vlie_session_id: str = "", meta: dict[str, Any] | None = None) -> dict[str, Any]:
    sid = f"alcis_{uuid.uuid4().hex[:12]}"
    doc = {
        "session_id": sid,
        "learner_id": learner_id,
        "companion_id": companion_id,
        "vlie_session_id": vlie_session_id,
        "messages": [],
        "meta": meta or {},
        "created_at": _now(),
        "status": "active",
    }
    _path(sid).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc


def load_session(session_id: str) -> dict[str, Any] | None:
    p = _path(session_id)
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def append_message(session_id: str, message: dict[str, Any]) -> dict[str, Any]:
    doc = load_session(session_id)
    if not doc:
        raise FileNotFoundError(session_id)
    doc.setdefault("messages", []).append({**message, "ts": _now()})
    doc["messages"] = doc["messages"][-100:]
    _path(session_id).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc


def end_session(session_id: str) -> dict[str, Any]:
    doc = load_session(session_id)
    if not doc:
        return {"ok": False, "error": "not_found"}
    doc["status"] = "closed"
    doc["ended_at"] = _now()
    _path(session_id).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"ok": True, "session": doc}
