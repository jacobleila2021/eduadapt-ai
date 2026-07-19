"""VMLE session memory — voice/read-along state persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from knowledge.paths import DATA_DIR

from engines.voice_multimodal_learning.schemas import VoiceSession

SESSIONS_DIR = DATA_DIR / "vmle" / "sessions"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(session_id: str) -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in session_id)[:80]
    return SESSIONS_DIR / f"{safe}.json"


def start_session(
    learner_id: str,
    *,
    lesson_id: str = "",
    vlie_session_id: str = "",
    language: str = "en",
    voice_style: str = "Female",
    teacher_controls: dict[str, Any] | None = None,
    parent_controls: dict[str, Any] | None = None,
    accessibility: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sid = f"vmle_{uuid.uuid4().hex[:12]}"
    session = VoiceSession(
        session_id=sid,
        learner_id=learner_id,
        lesson_id=lesson_id,
        vlie_session_id=vlie_session_id,
        language=language,
        voice_style=voice_style,
        teacher_controls=teacher_controls or {"narration": True, "pronunciation": True, "interactive": True},
        parent_controls=parent_controls or {"enable_narration": True, "view_audio_usage": True},
        accessibility=accessibility or {},
        created_at=_now(),
    )
    doc = session.to_dict()
    doc["read_along"] = {}
    doc["events"] = []
    _path(sid).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc


def load_session(session_id: str) -> dict[str, Any] | None:
    p = _path(session_id)
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def save_session(doc: dict[str, Any]) -> dict[str, Any]:
    doc["updated_at"] = _now()
    _path(doc["session_id"]).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc


def end_session(session_id: str) -> dict[str, Any]:
    doc = load_session(session_id)
    if not doc:
        return {"ok": False, "error": "not_found"}
    doc["status"] = "closed"
    doc["ended_at"] = _now()
    save_session(doc)
    return {"ok": True, "session": doc}


def update_bookmark(session_id: str, bookmark: dict[str, Any]) -> dict[str, Any]:
    doc = load_session(session_id)
    if not doc:
        return {"ok": False, "error": "not_found"}
    doc["bookmark"] = bookmark
    save_session(doc)
    return {"ok": True, "session": doc}
