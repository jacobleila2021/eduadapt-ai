"""Advanced offline sync — delta packages, conflict queue, retries (Phase 4)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import uuid

from knowledge.paths import DATA_DIR

from engines.learning_experience_platform.offline import OFFLINE_DIR, cache_lesson, sync_cache

SYNC_DIR = DATA_DIR / "lxp" / "sync"
QUEUE_PATH = SYNC_DIR / "queue.json"
PACKAGES_DIR = SYNC_DIR / "packages"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def build_full_package(
    *,
    learner_id: str,
    lesson_id: str,
    lesson_payload: dict[str, Any],
    notes: list | None = None,
    highlights: list | None = None,
    bookmarks: list | None = None,
    comments: list | None = None,
    flashcards: list | None = None,
    revision_plan: dict | None = None,
    voice: dict | None = None,
    glossary: list | None = None,
    companion_memory: dict | None = None,
    preferences: dict | None = None,
    progress: dict | None = None,
) -> dict[str, Any]:
    """Full offline lesson package — curriculum payload must already be verified."""
    PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    pid = f"pkg_{uuid.uuid4().hex[:10]}"
    doc = {
        "package_id": pid,
        "learner_id": learner_id,
        "lesson_id": lesson_id,
        "version": 1,
        "created_at": _now(),
        "lesson_payload": lesson_payload,
        "notes": notes or [],
        "highlights": highlights or [],
        "bookmarks": bookmarks or [],
        "comments": comments or [],
        "flashcards": flashcards or [],
        "revision_plan": revision_plan or {},
        "voice": voice or {},
        "glossary": glossary or [],
        "companion_memory": companion_memory or {},
        "preferences": preferences or {},
        "progress": progress or {},
        "policy": {"verified_curriculum_only": True, "never_invent_offline_content": True},
    }
    path = PACKAGES_DIR / f"{pid}.json"
    _save(path, doc)
    # Also seed Phase 1 cache for back-compat
    cache_lesson(
        learner_id=learner_id,
        lesson_id=lesson_id,
        lesson_payload=lesson_payload,
        notes=notes,
        bookmarks=bookmarks,
        highlights=highlights,
        progress=progress,
        audio_meta=voice,
    )
    return {"ok": True, "package_id": pid, "path": str(path), "size_estimate_bytes": path.stat().st_size}


def enqueue_delta(learner_id: str, entity: str, entity_id: str, op: str, payload: dict[str, Any]) -> dict[str, Any]:
    SYNC_DIR.mkdir(parents=True, exist_ok=True)
    queue = _load(QUEUE_PATH, {"items": []})
    item = {
        "queue_id": f"q_{uuid.uuid4().hex[:8]}",
        "learner_id": learner_id,
        "entity": entity,
        "entity_id": entity_id,
        "op": op,
        "payload": payload,
        "enqueued_at": _now(),
        "retries": 0,
        "status": "pending",
    }
    queue["items"].append(item)
    queue["items"] = queue["items"][-500:]
    _save(QUEUE_PATH, queue)
    return {"ok": True, "item": item}


def sync_status(learner_id: str = "") -> dict[str, Any]:
    queue = _load(QUEUE_PATH, {"items": []})
    items = queue.get("items") or []
    if learner_id:
        items = [i for i in items if i.get("learner_id") == learner_id]
    pending = [i for i in items if i.get("status") == "pending"]
    conflicts = [i for i in items if i.get("status") == "conflict"]
    return {
        "ok": True,
        "state": "conflict" if conflicts else ("syncing" if pending else "synced" if items else "idle"),
        "pending": len(pending),
        "conflicts": conflicts[-20:],
        "queue_size": len(items),
        "last_synced_at": next((i.get("synced_at") for i in reversed(items) if i.get("status") == "synced"), ""),
    }


def detect_conflict(local: dict[str, Any], remote: dict[str, Any], *, key: str = "updated_at") -> dict[str, Any]:
    lv = str(local.get(key) or local.get("version") or "")
    rv = str(remote.get(key) or remote.get("version") or "")
    if lv and rv and lv != rv:
        return {
            "conflict": True,
            "local": local,
            "remote": remote,
            "strategy_options": ["local_wins", "remote_wins", "merge_by_timestamp", "manual"],
        }
    return {"conflict": False}


def resolve_conflict(
    local: dict[str, Any],
    remote: dict[str, Any],
    *,
    strategy: str = "merge_by_timestamp",
    key: str = "updated_at",
) -> dict[str, Any]:
    if strategy == "local_wins":
        return {"ok": True, "resolved": local, "strategy": strategy}
    if strategy == "remote_wins":
        return {"ok": True, "resolved": remote, "strategy": strategy}
    # merge_by_timestamp / default
    if str(remote.get(key) or "") > str(local.get(key) or ""):
        merged = {**local, **remote, "conflict_resolution": "remote_newer"}
    else:
        merged = {**remote, **local, "conflict_resolution": "local_newer"}
    # Prefer higher reading_pct when both have it
    if "reading_pct" in local or "reading_pct" in remote:
        merged["reading_pct"] = max(float(local.get("reading_pct") or 0), float(remote.get("reading_pct") or 0))
    return {"ok": True, "resolved": merged, "strategy": strategy}


def process_queue(*, max_items: int = 20, auto_retry: bool = True) -> dict[str, Any]:
    queue = _load(QUEUE_PATH, {"items": []})
    processed = []
    for item in list(queue.get("items") or []):
        if item.get("status") != "pending":
            continue
        if len(processed) >= max_items:
            break
        try:
            # Apply delta: for progress entities, use Phase 1 sync helpers when cache_id present
            payload = item.get("payload") or {}
            if item.get("entity") == "progress" and payload.get("cache_id"):
                sync_cache(str(payload["cache_id"]), server_progress=payload.get("server_progress"))
            item["status"] = "synced"
            item["synced_at"] = _now()
            processed.append(item["queue_id"])
        except Exception as exc:  # noqa: BLE001
            item["retries"] = int(item.get("retries") or 0) + 1
            item["last_error"] = str(exc)
            if auto_retry and item["retries"] < 5:
                item["status"] = "pending"
            else:
                item["status"] = "error"
    _save(QUEUE_PATH, queue)
    return {"ok": True, "processed": processed, "status": sync_status()}


def storage_optimization_report(learner_id: str = "") -> dict[str, Any]:
    total = 0
    files = 0
    for root in (OFFLINE_DIR, PACKAGES_DIR, SYNC_DIR):
        if not root.exists():
            continue
        for p in root.rglob("*.json"):
            if learner_id and learner_id not in p.read_text(encoding="utf-8", errors="ignore")[:500]:
                # cheap filter — skip full scan cost for unrelated
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    if data.get("learner_id") and data.get("learner_id") != learner_id:
                        continue
                except Exception:  # noqa: BLE001
                    pass
            total += p.stat().st_size
            files += 1
    return {
        "ok": True,
        "files": files,
        "bytes": total,
        "mb": round(total / (1024 * 1024), 3),
        "tips": ["prune synced packages older than 30 days", "compress voice downloads", "dedupe glossary"],
    }


def background_sync(learner_id: str = "") -> dict[str, Any]:
    """Background sync entry — processes queue + reports status."""
    out = process_queue()
    status = sync_status(learner_id)
    from engines.learning_experience_platform import analytics

    analytics.track("offline_sync", learner_id=learner_id, payload={"status": status.get("state"), "processed": out.get("processed")})
    return {"ok": True, "background": True, "result": out, "status": status}
