"""Monitoring — import health, errors, index stats."""

from __future__ import annotations

from typing import Any

from engines.curriculum_migration_framework.indexer import search_index
from engines.curriculum_migration_framework.migration import list_jobs
from engines.curriculum_migration_framework.scheduler import queue_status


def monitoring_snapshot() -> dict[str, Any]:
    jobs = list_jobs(100)
    by_status: dict[str, int] = {}
    errors = []
    scores = []
    for j in jobs:
        st = str(j.get("status") or "unknown")
        by_status[st] = by_status.get(st, 0) + 1
        if j.get("errors"):
            errors.append({"job_id": j.get("job_id"), "errors": j.get("errors")})
        if j.get("quality_score") is not None:
            scores.append(float(j["quality_score"]))
    idx = search_index(limit=1)
    return {
        "ok": True,
        "jobs_by_status": by_status,
        "import_errors": errors[:20],
        "avg_quality_score": round(sum(scores) / len(scores), 3) if scores else None,
        "queue": queue_status(),
        "index_health": {"search_ok": idx.get("ok"), "sample_hits": idx.get("count")},
    }
