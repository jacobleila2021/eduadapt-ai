"""CMIF versioning — never overwrite published packages; support rollback."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from knowledge.paths import DATA_DIR

from engines.curriculum_migration_framework.schemas import PACKAGE_LIFECYCLE

VERSIONS_DIR = DATA_DIR / "cmif" / "versions"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe(s: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in s)[:100]


def bump_semver(version: str, *, level: str = "patch") -> str:
    parts = [int(x) if str(x).isdigit() else 0 for x in (version or "0.0.0").split(".")[:3]]
    while len(parts) < 3:
        parts.append(0)
    major, minor, patch = parts
    if level == "major":
        major, minor, patch = major + 1, 0, 0
    elif level == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    return f"{major}.{minor}.{patch}"


def save_version(
    package_id: str,
    package: dict[str, Any],
    *,
    status: str = "draft",
    note: str = "",
) -> dict[str, Any]:
    status = status if status in PACKAGE_LIFECYCLE else "draft"
    root = VERSIONS_DIR / _safe(package_id)
    root.mkdir(parents=True, exist_ok=True)
    hist_path = root / "history.json"
    history = json.loads(hist_path.read_text(encoding="utf-8")) if hist_path.is_file() else []

    # Never overwrite published snapshots
    published = [h for h in history if h.get("status") == "published"]
    ver = str(package.get("version") or "1.0.0")
    if published and status == "published":
        ver = bump_semver(published[-1].get("version") or ver, level="minor")

    vid = f"cmifv_{uuid.uuid4().hex[:10]}"
    snap_path = root / f"{vid}.json"
    doc = {
        **package,
        "version": ver,
        "lifecycle_status": status,
        "version_id": vid,
        "immutable": status == "published",
        "snapshotted_at": _now(),
        "note": note,
    }
    snap_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    history.append({
        "version_id": vid,
        "version": ver,
        "status": status,
        "path": str(snap_path),
        "at": _now(),
        "note": note,
        "immutable": status == "published",
    })
    hist_path.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"ok": True, "version_id": vid, "version": ver, "status": status, "path": str(snap_path)}


def version_history(package_id: str) -> dict[str, Any]:
    hist_path = VERSIONS_DIR / _safe(package_id) / "history.json"
    if not hist_path.is_file():
        return {"ok": True, "package_id": package_id, "history": []}
    return {"ok": True, "package_id": package_id, "history": json.loads(hist_path.read_text(encoding="utf-8"))}


def load_version(package_id: str, version_id: str) -> dict[str, Any] | None:
    hist = version_history(package_id).get("history") or []
    for h in hist:
        if h.get("version_id") == version_id:
            path = Path(h["path"])
            if path.is_file():
                return json.loads(path.read_text(encoding="utf-8"))
    return None


def rollback(package_id: str, version_id: str) -> dict[str, Any]:
    doc = load_version(package_id, version_id)
    if not doc:
        return {"ok": False, "error": "version_not_found"}
    # Create new draft from historical snapshot — never mutate published file
    return save_version(package_id, {**doc, "rolled_back_from": version_id}, status="draft", note=f"rollback:{version_id}")


def archive_package(package_id: str) -> dict[str, Any]:
    hist = version_history(package_id).get("history") or []
    if not hist:
        return {"ok": False, "error": "no_versions"}
    latest = load_version(package_id, hist[-1]["version_id"]) or {}
    return save_version(package_id, latest, status="archived", note="archive")
