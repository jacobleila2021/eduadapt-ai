"""Administrative dashboard for CMIF."""

from __future__ import annotations

from typing import Any

from engines.curriculum_migration_framework.migration import list_jobs
from engines.curriculum_migration_framework.monitoring import monitoring_snapshot
from engines.curriculum_migration_framework.schemas import SUPPORTED_BOARDS
from engines.curriculum_migration_framework.versioning import version_history


def admin_dashboard() -> dict[str, Any]:
    jobs = list_jobs(100)
    coverage_board: dict[str, int] = {}
    coverage_subject: dict[str, int] = {}
    coverage_grade: dict[str, int] = {}
    missing_meta = []
    validation = {"passed": 0, "rejected": 0, "failed": 0}
    pub = {"published": 0, "draft": 0, "other": 0}

    for j in jobs:
        b = str(j.get("board") or "unknown")
        coverage_board[b] = coverage_board.get(b, 0) + 1
        st = j.get("status")
        if st == "completed":
            validation["passed"] += 1
            pub["published"] += 1
        elif st == "rejected":
            validation["rejected"] += 1
        elif st == "failed":
            validation["failed"] += 1
        arts = j.get("artifacts") or {}
        norm = arts.get("normalize") or {}
        if isinstance(norm, dict):
            sub = str(norm.get("subject") or "")
            gr = str(norm.get("grade") or "")
            if sub:
                coverage_subject[sub] = coverage_subject.get(sub, 0) + 1
            if gr:
                coverage_grade[gr] = coverage_grade.get(gr, 0) + 1
            if not norm.get("source_hash") and not (arts.get("provenance") or {}).get("source_hash"):
                missing_meta.append(j.get("job_id"))

    mon = monitoring_snapshot()
    sample_versions = {}
    for j in jobs[:5]:
        pid = j.get("package_id") or j.get("job_id")
        if pid:
            sample_versions[pid] = (version_history(str(pid)).get("history") or [])[-3:]

    return {
        "ok": True,
        "import_queue": mon.get("queue"),
        "validation_status": validation,
        "coverage_by_board": coverage_board,
        "coverage_by_subject": coverage_subject,
        "coverage_by_grade": coverage_grade,
        "version_history": sample_versions,
        "publication_status": pub,
        "import_errors": mon.get("import_errors"),
        "missing_metadata": missing_meta[:20],
        "quality_score": mon.get("avg_quality_score"),
        "index_health": mon.get("index_health"),
        "supported_boards": list(SUPPORTED_BOARDS),
        "roadmap": [
            "Phase1 Framework",
            "Phase2 NCERT+CBSE pilot",
            "Phase3 Indian boards",
            "Phase4 Cambridge+IB",
            "Phase5 Higher ed + professional",
        ],
    }
