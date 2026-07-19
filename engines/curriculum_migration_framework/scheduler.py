"""Background job scheduler — queue, batch, resume."""

from __future__ import annotations

from typing import Any
import uuid

from engines.curriculum_migration_framework.migration import load_job, run_migration

_QUEUE: list[dict[str, Any]] = []


def enqueue(job_spec: dict[str, Any]) -> dict[str, Any]:
    item = {"queue_id": f"q_{uuid.uuid4().hex[:8]}", "status": "queued", "spec": job_spec}
    _QUEUE.append(item)
    return {"ok": True, "item": item, "queue_depth": len(_QUEUE)}


def process_queue(*, max_jobs: int = 3, parallel: bool = False) -> dict[str, Any]:
    """Process queued imports. parallel flag reserved — sequential for determinism."""
    _ = parallel
    processed = []
    for item in list(_QUEUE):
        if item.get("status") != "queued":
            continue
        if len(processed) >= max_jobs:
            break
        item["status"] = "running"
        spec = item.get("spec") or {}
        result = run_migration(**{k: spec[k] for k in spec if k in (
            "board", "path", "inline", "source_type", "source_url", "expected_checksum",
            "publisher", "publish", "role", "resume_job_id", "lazy_index", "meta",
        )})
        item["status"] = "completed" if result.get("ok") else "failed"
        item["result"] = {"ok": result.get("ok"), "job_id": (result.get("job") or {}).get("job_id"), "package_id": result.get("package_id")}
        processed.append(item)
    # trim finished
    remaining = [i for i in _QUEUE if i.get("status") == "queued"]
    _QUEUE.clear()
    _QUEUE.extend(remaining)
    return {"ok": True, "processed": processed, "remaining": len(_QUEUE)}


def resume_job(job_id: str, **kwargs: Any) -> dict[str, Any]:
    job = load_job(job_id)
    if not job:
        return {"ok": False, "error": "job_not_found"}
    return run_migration(
        board=str(job.get("board") or kwargs.get("board") or "cbse"),
        resume_job_id=job_id,
        inline=kwargs.get("inline"),
        publish=bool(kwargs.get("publish", True)),
        role=str(kwargs.get("role") or "system"),
    )


def queue_status() -> dict[str, Any]:
    return {
        "ok": True,
        "queued": sum(1 for i in _QUEUE if i.get("status") == "queued"),
        "items": list(_QUEUE)[-20:],
    }
