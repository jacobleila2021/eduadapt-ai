"""Package / topic metadata helpers & versioning."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework.curriculum_registry import deprecate_package, load_package, save_package


def curriculum_metadata(package_id: str) -> dict[str, Any]:
    doc = load_package(package_id)
    if not doc:
        return {"ok": False, "error": "not_found"}
    return {
        "ok": True,
        "package_id": package_id,
        "board": doc.get("board"),
        "structure": doc.get("structure"),
        "version": doc.get("version"),
        "status": doc.get("status"),
        "supersedes": doc.get("supersedes"),
        "topic_count": len(doc.get("topics") or []),
        "schema": doc.get("schema") or "ucf/1.0",
    }


def migrate_version(package_id: str, new_version: str, *, changes: dict[str, Any] | None = None) -> dict[str, Any]:
    doc = load_package(package_id)
    if not doc:
        return {"ok": False, "error": "not_found"}
    old_version = doc.get("version")
    new_id = f"{package_id}_v{new_version.replace('.', '_')}"
    new_doc = dict(doc)
    new_doc["package_id"] = new_id
    new_doc["version"] = new_version
    new_doc["supersedes"] = package_id
    if changes:
        new_doc.update(changes)
    save_package(new_doc)
    deprecate_package(package_id, superseding=new_id)
    return {"ok": True, "from": package_id, "to": new_id, "old_version": old_version, "new_version": new_version}
