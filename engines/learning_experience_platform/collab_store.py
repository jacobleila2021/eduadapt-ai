"""LXP Phase 3 collaboration persistence (comments, annotations, notifications)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from knowledge.paths import DATA_DIR

COLLAB_DIR = DATA_DIR / "lxp" / "collaboration"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in s)[:100]


def _lesson_dir(lesson_id: str) -> Path:
    path = COLLAB_DIR / "lessons" / _safe(lesson_id)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_comments(lesson_id: str) -> list[dict[str, Any]]:
    return list(_load(_lesson_dir(lesson_id) / "comments.json", []))


def save_comments(lesson_id: str, comments: list[dict[str, Any]]) -> None:
    _save(_lesson_dir(lesson_id) / "comments.json", comments)


def append_comment(lesson_id: str, comment: dict[str, Any]) -> dict[str, Any]:
    rows = load_comments(lesson_id)
    if not comment.get("comment_id"):
        comment["comment_id"] = f"c_{uuid.uuid4().hex[:10]}"
    comment.setdefault("created_at", _now())
    comment["updated_at"] = _now()
    rows.append(comment)
    save_comments(lesson_id, rows)
    return comment


def update_comment(lesson_id: str, comment_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    rows = load_comments(lesson_id)
    for i, c in enumerate(rows):
        if c.get("comment_id") == comment_id:
            rows[i] = {**c, **patch, "updated_at": _now()}
            save_comments(lesson_id, rows)
            return {"ok": True, "comment": rows[i]}
    return {"ok": False, "error": "comment_not_found"}


def load_annotations(lesson_id: str) -> list[dict[str, Any]]:
    return list(_load(_lesson_dir(lesson_id) / "annotations.json", []))


def save_annotations(lesson_id: str, rows: list[dict[str, Any]]) -> None:
    _save(_lesson_dir(lesson_id) / "annotations.json", rows)


def upsert_annotation(lesson_id: str, annotation: dict[str, Any]) -> dict[str, Any]:
    rows = load_annotations(lesson_id)
    aid = annotation.get("annotation_id") or f"a_{uuid.uuid4().hex[:10]}"
    annotation["annotation_id"] = aid
    now = _now()
    for i, a in enumerate(rows):
        if a.get("annotation_id") == aid:
            hist = list(a.get("history") or [])
            hist.append({"version": a.get("version", 1), "payload": a.get("payload"), "at": a.get("updated_at")})
            version = int(a.get("version") or 1) + 1
            rows[i] = {
                **a,
                **annotation,
                "version": version,
                "history": hist[-20:],
                "updated_at": now,
            }
            save_annotations(lesson_id, rows)
            return rows[i]
    annotation.setdefault("version", 1)
    annotation.setdefault("history", [])
    annotation.setdefault("created_at", now)
    annotation["updated_at"] = now
    rows.append(annotation)
    save_annotations(lesson_id, rows)
    return annotation


def load_notifications(user_id: str) -> list[dict[str, Any]]:
    path = COLLAB_DIR / "notifications" / f"{_safe(user_id)}.json"
    return list(_load(path, []))


def push_notification(user_id: str, event: dict[str, Any]) -> dict[str, Any]:
    path = COLLAB_DIR / "notifications" / f"{_safe(user_id)}.json"
    rows = load_notifications(user_id)
    event = {**event, "notification_id": event.get("notification_id") or f"n_{uuid.uuid4().hex[:8]}", "created_at": _now(), "read": False}
    rows.insert(0, event)
    _save(path, rows[:200])
    return event


def load_workspace_notes(role: str, user_id: str, lesson_id: str = "") -> list[dict[str, Any]]:
    path = COLLAB_DIR / "workspace_notes" / _safe(role) / f"{_safe(user_id)}.json"
    rows = list(_load(path, []))
    if lesson_id:
        rows = [r for r in rows if r.get("lesson_id") == lesson_id]
    return rows


def save_workspace_note(role: str, user_id: str, note: dict[str, Any]) -> dict[str, Any]:
    path = COLLAB_DIR / "workspace_notes" / _safe(role) / f"{_safe(user_id)}.json"
    rows = list(_load(path, []))
    if not note.get("note_id"):
        note["note_id"] = f"wn_{uuid.uuid4().hex[:8]}"
    note.setdefault("created_at", _now())
    note["updated_at"] = _now()
    rows.append(note)
    _save(path, rows)
    return note
