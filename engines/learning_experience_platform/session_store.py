"""LXP session & learner annotation persistence."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from knowledge.paths import DATA_DIR

LXP_DIR = DATA_DIR / "lxp"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _learner_dir(learner_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in learner_id)[:80]
    path = LXP_DIR / "learners" / safe
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_preferences(learner_id: str) -> dict[str, Any]:
    from engines.learning_experience_platform.schemas import ReaderPreferences

    path = _learner_dir(learner_id) / "preferences.json"
    data = _load(path, None)
    if not data:
        data = ReaderPreferences().to_dict()
        _save(path, data)
    return data


def save_preferences(learner_id: str, prefs: dict[str, Any]) -> dict[str, Any]:
    path = _learner_dir(learner_id) / "preferences.json"
    prefs = {**load_preferences(learner_id), **prefs, "updated_at": _now()}
    _save(path, prefs)
    return prefs


def load_progress(learner_id: str, lesson_id: str) -> dict[str, Any]:
    path = _learner_dir(learner_id) / "progress.json"
    all_p = _load(path, {})
    return all_p.get(lesson_id) or {
        "lesson_id": lesson_id,
        "completion_pct": 0.0,
        "reading_pct": 0.0,
        "estimated_minutes": 0.0,
        "time_spent_seconds": 0.0,
        "resume_offset": 0,
        "resume_anchor": "",
        "last_viewed_at": "",
    }


def save_progress(learner_id: str, lesson_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    path = _learner_dir(learner_id) / "progress.json"
    all_p = _load(path, {})
    row = {**load_progress(learner_id, lesson_id), **patch, "lesson_id": lesson_id, "last_viewed_at": _now()}
    all_p[lesson_id] = row
    # recently viewed
    recent = list(all_p.get("_recent") or [])
    recent = [x for x in recent if x != lesson_id]
    recent.insert(0, lesson_id)
    all_p["_recent"] = recent[:20]
    _save(path, all_p)
    return row


def list_recent_lessons(learner_id: str) -> list[str]:
    path = _learner_dir(learner_id) / "progress.json"
    return list(_load(path, {}).get("_recent") or [])


def list_notes(learner_id: str, lesson_id: str = "") -> list[dict[str, Any]]:
    path = _learner_dir(learner_id) / "notes.json"
    notes = _load(path, [])
    if lesson_id:
        notes = [n for n in notes if n.get("lesson_id") == lesson_id]
    return notes


def upsert_note(learner_id: str, note: dict[str, Any]) -> dict[str, Any]:
    path = _learner_dir(learner_id) / "notes.json"
    notes = _load(path, [])
    nid = note.get("note_id") or f"note_{uuid.uuid4().hex[:10]}"
    now = _now()
    row = {
        "note_id": nid,
        "lesson_id": note.get("lesson_id") or "",
        "text": note.get("text") or "",
        "category": note.get("category") or "general",
        "anchor": note.get("anchor") or "",
        "created_at": note.get("created_at") or now,
        "updated_at": now,
    }
    notes = [n for n in notes if n.get("note_id") != nid] + [row]
    _save(path, notes)
    return row


def delete_note(learner_id: str, note_id: str) -> dict[str, Any]:
    path = _learner_dir(learner_id) / "notes.json"
    notes = _load(path, [])
    before = len(notes)
    notes = [n for n in notes if n.get("note_id") != note_id]
    _save(path, notes)
    return {"ok": before != len(notes), "note_id": note_id}


def search_notes(learner_id: str, query: str) -> list[dict[str, Any]]:
    q = (query or "").lower()
    return [n for n in list_notes(learner_id) if q in str(n.get("text") or "").lower() or q in str(n.get("category") or "").lower()]


def list_highlights(learner_id: str, lesson_id: str = "") -> list[dict[str, Any]]:
    path = _learner_dir(learner_id) / "highlights.json"
    rows = _load(path, [])
    if lesson_id:
        rows = [h for h in rows if h.get("lesson_id") == lesson_id]
    return rows


def add_highlight(learner_id: str, highlight: dict[str, Any]) -> dict[str, Any]:
    from engines.learning_experience_platform.schemas import HIGHLIGHT_COLORS

    path = _learner_dir(learner_id) / "highlights.json"
    rows = _load(path, [])
    color = highlight.get("color") or "yellow"
    if color not in HIGHLIGHT_COLORS:
        color = "yellow"
    row = {
        "highlight_id": highlight.get("highlight_id") or f"hl_{uuid.uuid4().hex[:10]}",
        "lesson_id": highlight.get("lesson_id") or "",
        "color": color,
        "label": highlight.get("label") or "",
        "target_type": highlight.get("target_type") or "text",
        "anchor": highlight.get("anchor") or "",
        "excerpt": highlight.get("excerpt") or "",
        "created_at": _now(),
    }
    rows.append(row)
    _save(path, rows)
    return row


def delete_highlight(learner_id: str, highlight_id: str) -> dict[str, Any]:
    path = _learner_dir(learner_id) / "highlights.json"
    rows = _load(path, [])
    before = len(rows)
    rows = [h for h in rows if h.get("highlight_id") != highlight_id]
    _save(path, rows)
    return {"ok": before != len(rows)}


def list_bookmarks(learner_id: str, folder: str = "") -> list[dict[str, Any]]:
    path = _learner_dir(learner_id) / "bookmarks.json"
    rows = _load(path, [])
    if folder:
        rows = [b for b in rows if b.get("folder") == folder]
    return rows


def add_bookmark(learner_id: str, bookmark: dict[str, Any]) -> dict[str, Any]:
    path = _learner_dir(learner_id) / "bookmarks.json"
    rows = _load(path, [])
    row = {
        "bookmark_id": bookmark.get("bookmark_id") or f"bm_{uuid.uuid4().hex[:10]}",
        "lesson_id": bookmark.get("lesson_id") or "",
        "target_type": bookmark.get("target_type") or "lesson",
        "anchor": bookmark.get("anchor") or "",
        "folder": bookmark.get("folder") or "default",
        "label": bookmark.get("label") or "",
        "created_at": _now(),
    }
    rows.append(row)
    _save(path, rows)
    return row


def delete_bookmark(learner_id: str, bookmark_id: str) -> dict[str, Any]:
    path = _learner_dir(learner_id) / "bookmarks.json"
    rows = _load(path, [])
    before = len(rows)
    rows = [b for b in rows if b.get("bookmark_id") != bookmark_id]
    _save(path, rows)
    return {"ok": before != len(rows)}
