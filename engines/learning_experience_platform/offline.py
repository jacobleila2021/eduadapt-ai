"""Offline lesson cache + sync with conflict-safe merge."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from knowledge.paths import DATA_DIR

OFFLINE_DIR = DATA_DIR / "lxp" / "offline"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def cache_lesson(
    *,
    learner_id: str,
    lesson_id: str,
    lesson_payload: dict[str, Any],
    notes: list[dict[str, Any]] | None = None,
    bookmarks: list[dict[str, Any]] | None = None,
    highlights: list[dict[str, Any]] | None = None,
    progress: dict[str, Any] | None = None,
    audio_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    OFFLINE_DIR.mkdir(parents=True, exist_ok=True)
    cid = f"off_{uuid.uuid4().hex[:10]}"
    path = OFFLINE_DIR / f"{cid}.json"
    doc = {
        "cache_id": cid,
        "learner_id": learner_id,
        "lesson_id": lesson_id,
        "lesson_payload": lesson_payload,
        "notes": notes or [],
        "bookmarks": bookmarks or [],
        "highlights": highlights or [],
        "progress": progress or {},
        "audio_meta": audio_meta or {},
        "cached_at": _now(),
        "synced": False,
        "version": 1,
    }
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"ok": True, "cache_id": cid, "path": str(path)}


def sync_cache(cache_id: str, *, server_progress: dict[str, Any] | None = None) -> dict[str, Any]:
    path = OFFLINE_DIR / f"{cache_id}.json"
    if not path.is_file():
        return {"ok": False, "error": "not_found"}
    doc = json.loads(path.read_text(encoding="utf-8"))
    local = doc.get("progress") or {}
    server = server_progress or {}
    # Conflict-safe: keep higher reading_pct / later timestamp
    merged = dict(local)
    if float(server.get("reading_pct") or 0) > float(local.get("reading_pct") or 0):
        merged["reading_pct"] = server["reading_pct"]
        merged["conflict_resolution"] = "server_ahead"
    elif float(local.get("reading_pct") or 0) > float(server.get("reading_pct") or 0):
        merged["conflict_resolution"] = "local_ahead"
    else:
        merged["conflict_resolution"] = "equal"
    # Prefer later last_viewed_at
    if str(server.get("last_viewed_at") or "") > str(local.get("last_viewed_at") or ""):
        merged["last_viewed_at"] = server.get("last_viewed_at")
        if merged.get("conflict_resolution") == "equal":
            merged["conflict_resolution"] = "server_newer_ts"
    doc["progress"] = merged
    doc["synced"] = True
    doc["synced_at"] = _now()
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    # Apply to session store when possible
    try:
        from engines.learning_experience_platform.session_store import save_progress

        save_progress(doc["learner_id"], doc["lesson_id"], merged)
        for n in doc.get("notes") or []:
            from engines.learning_experience_platform.session_store import upsert_note

            upsert_note(doc["learner_id"], n)
    except Exception:  # noqa: BLE001
        pass
    return {"ok": True, "cache_id": cache_id, "progress": merged, "synced": True}
