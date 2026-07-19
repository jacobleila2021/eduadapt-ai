"""Curriculum package versioning — drafts, publish, rollback, history."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from knowledge.paths import DATA_DIR

VERSIONS_DIR = DATA_DIR / "cef" / "versions"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hist_path(curriculum_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in curriculum_id)[:80]
    return VERSIONS_DIR / safe / "history.json"


def _snap_dir(curriculum_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in curriculum_id)[:80]
    path = VERSIONS_DIR / safe / "snapshots"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _load_history(curriculum_id: str) -> list[dict[str, Any]]:
    path = _hist_path(curriculum_id)
    if not path.is_file():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _save_history(curriculum_id: str, rows: list[dict[str, Any]]) -> None:
    path = _hist_path(curriculum_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")


def snapshot(
    curriculum_id: str,
    package: dict[str, Any],
    *,
    version: str = "",
    status: str = "draft",
    note: str = "",
) -> dict[str, Any]:
    ver = version or str(package.get("version") or f"1.0.{len(_load_history(curriculum_id))}")
    sid = f"v_{uuid.uuid4().hex[:8]}"
    path = _snap_dir(curriculum_id) / f"{sid}.json"
    doc = {**package, "version": ver, "cef_status": status, "snapshot_id": sid, "snapshotted_at": _now()}
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    hist = _load_history(curriculum_id)
    hist.append({
        "snapshot_id": sid,
        "version": ver,
        "status": status,
        "note": note,
        "path": str(path),
        "at": _now(),
    })
    _save_history(curriculum_id, hist)
    return {"ok": True, "snapshot_id": sid, "version": ver, "path": str(path)}


def version_history(curriculum_id: str) -> dict[str, Any]:
    return {"ok": True, "curriculum_id": curriculum_id, "history": _load_history(curriculum_id)}


def compare_versions(curriculum_id: str, snapshot_a: str, snapshot_b: str) -> dict[str, Any]:
    hist = {h["snapshot_id"]: h for h in _load_history(curriculum_id)}
    a = hist.get(snapshot_a)
    b = hist.get(snapshot_b)
    if not a or not b:
        return {"ok": False, "error": "snapshot_not_found"}
    da = json.loads(Path(a["path"]).read_text(encoding="utf-8"))
    db = json.loads(Path(b["path"]).read_text(encoding="utf-8"))
    topics_a = {t.get("id") or t.get("topic_id") or t.get("title") for t in (da.get("topics") or da.get("concepts") or []) if isinstance(t, dict) or isinstance(t, str)}
    topics_b = {t.get("id") or t.get("topic_id") or t.get("title") for t in (db.get("topics") or db.get("concepts") or []) if isinstance(t, dict) or isinstance(t, str)}
    # normalize strings
    topics_a = {str(x) for x in topics_a if x}
    topics_b = {str(x) for x in topics_b if x}
    return {
        "ok": True,
        "added": sorted(topics_b - topics_a),
        "removed": sorted(topics_a - topics_b),
        "version_a": a.get("version"),
        "version_b": b.get("version"),
    }


def rollback(curriculum_id: str, snapshot_id: str) -> dict[str, Any]:
    hist = {h["snapshot_id"]: h for h in _load_history(curriculum_id)}
    target = hist.get(snapshot_id)
    if not target:
        return {"ok": False, "error": "snapshot_not_found"}
    src = Path(target["path"])
    if not src.is_file():
        return {"ok": False, "error": "snapshot_file_missing"}
    # Copy as new rollback snapshot
    doc = json.loads(src.read_text(encoding="utf-8"))
    return snapshot(curriculum_id, doc, version=str(doc.get("version") or target.get("version")), status="draft", note=f"rollback_from:{snapshot_id}")


def load_snapshot(curriculum_id: str, snapshot_id: str) -> dict[str, Any] | None:
    hist = {h["snapshot_id"]: h for h in _load_history(curriculum_id)}
    target = hist.get(snapshot_id)
    if not target:
        return None
    path = Path(target["path"])
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
