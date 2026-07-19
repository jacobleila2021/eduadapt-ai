"""Curriculum package registry — versioned UCF packages on disk."""

from __future__ import annotations

import json
import os
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

from engines.universal_curriculum_framework.schemas import UCFPackage

PACKAGES_DIR = DATA_DIR / "ucf" / "packages"
INDEX_PATH = DATA_DIR / "ucf" / "registry.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure() -> None:
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)


def save_package(package: UCFPackage | dict[str, Any]) -> dict[str, Any]:
    _ensure()
    doc = package.to_dict() if isinstance(package, UCFPackage) else dict(package)
    pid = doc["package_id"]
    path = PACKAGES_DIR / f"{pid}.json"
    _atomic_json_write(path, doc)
    index = _load_index()
    index[pid] = {
        "package_id": pid,
        "board_id": (doc.get("board") or {}).get("board_id"),
        "version": doc.get("version"),
        "status": doc.get("status"),
        "topics": len(doc.get("topics") or []),
        "path": str(path),
        "updated_at": _now(),
    }
    _save_index(index)
    return {"ok": True, "package_id": pid, "path": str(path)}


def load_package(package_id: str) -> dict[str, Any] | None:
    path = PACKAGES_DIR / f"{package_id}.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def list_packages(*, board_id: str = "", status: str = "active") -> list[dict[str, Any]]:
    index = _load_index()
    rows = list(index.values())
    if board_id:
        rows = [r for r in rows if r.get("board_id") == board_id]
    if status:
        rows = [r for r in rows if r.get("status") == status]
    return rows


def deprecate_package(package_id: str, *, superseding: str = "") -> dict[str, Any]:
    doc = load_package(package_id)
    if not doc:
        return {"ok": False, "error": "not_found"}
    doc["status"] = "deprecated"
    if superseding:
        doc["superseded_by"] = superseding
    return save_package(doc)


def _load_index() -> dict[str, Any]:
    _ensure()
    if not INDEX_PATH.is_file():
        return {}
    try:
        return json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _save_index(index: dict[str, Any]) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    _atomic_json_write(INDEX_PATH, index)


def _atomic_json_write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        last_error: PermissionError | None = None
        for attempt in range(8):
            try:
                os.replace(temporary, path)
                last_error = None
                break
            except PermissionError as exc:
                last_error = exc
                time.sleep(0.05 * (attempt + 1))
        if last_error is not None:
            # Windows may temporarily deny atomic replacement while another
            # reader has the registry open. A complete buffered rewrite is the
            # final compatibility fallback; readers tolerate transient JSON.
            path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
