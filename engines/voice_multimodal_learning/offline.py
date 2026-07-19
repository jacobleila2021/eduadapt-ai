"""Offline cache + sync when connectivity returns."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from knowledge.paths import DATA_DIR

OFFLINE_DIR = DATA_DIR / "vmle" / "offline"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def cache_lesson_bundle(
    *,
    learner_id: str,
    lesson_id: str,
    lesson_text: str = "",
    audio_meta: dict[str, Any] | None = None,
    images: list[str] | None = None,
    diagrams: list[dict[str, Any]] | None = None,
    assessments: list[dict[str, Any]] | None = None,
    session_state: dict[str, Any] | None = None,
    progress: dict[str, Any] | None = None,
) -> dict[str, Any]:
    OFFLINE_DIR.mkdir(parents=True, exist_ok=True)
    cid = f"off_{uuid.uuid4().hex[:10]}"
    path = OFFLINE_DIR / f"{cid}.json"
    doc = {
        "cache_id": cid,
        "learner_id": learner_id,
        "lesson_id": lesson_id,
        "lesson_text": lesson_text[:50000],
        "audio_meta": audio_meta or {},
        "images": images or [],
        "interactive_diagrams": diagrams or [],
        "assessments": assessments or [],
        "session_state": session_state or {},
        "progress": progress or {},
        "cached_at": _now(),
        "synced": False,
    }
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "cache_id": cid, "path": str(path)}


def list_cached(learner_id: str = "") -> list[dict[str, Any]]:
    if not OFFLINE_DIR.is_dir():
        return []
    rows = []
    for p in OFFLINE_DIR.glob("*.json"):
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            continue
        if learner_id and doc.get("learner_id") != learner_id:
            continue
        rows.append({"cache_id": doc.get("cache_id"), "lesson_id": doc.get("lesson_id"), "synced": doc.get("synced")})
    return rows


def synchronize(cache_id: str) -> dict[str, Any]:
    path = OFFLINE_DIR / f"{cache_id}.json"
    if not path.is_file():
        return {"ok": False, "error": "not_found"}
    doc = json.loads(path.read_text(encoding="utf-8"))
    doc["synced"] = True
    doc["synced_at"] = _now()
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "cache_id": cache_id, "synced": True, "events_to_vlie": ["SessionRestored"], "events_to_laie": True}
