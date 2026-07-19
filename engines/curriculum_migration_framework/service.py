"""REST-shaped API facade for Curriculum Migration & Ingestion Framework."""

from __future__ import annotations

from typing import Any

from engines.curriculum_migration_framework.dashboard import admin_dashboard
from engines.curriculum_migration_framework.indexer import search_index
from engines.curriculum_migration_framework.mapper import cross_board_compare
from engines.curriculum_migration_framework.migration import list_jobs, load_job, run_migration
from engines.curriculum_migration_framework.schemas import SUPPORTED_BOARDS
from engines.curriculum_migration_framework.scheduler import enqueue, process_queue, queue_status, resume_job
from engines.curriculum_migration_framework.validator import validate_package
from engines.curriculum_migration_framework.versioning import archive_package, rollback, version_history


def api_list_supported_boards() -> dict[str, Any]:
    return {"ok": True, "boards": list(SUPPORTED_BOARDS)}


def api_import_curriculum(**kwargs: Any) -> dict[str, Any]:
    return run_migration(**{k: kwargs[k] for k in kwargs if k in (
        "board", "path", "inline", "source_type", "source_url", "expected_checksum",
        "publisher", "publish", "role", "resume_job_id", "lazy_index", "meta",
    )})


def api_validate_curriculum(package: dict[str, Any], provenance: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"ok": True, "validation": validate_package(package, provenance=provenance)}


def api_publish_curriculum(**kwargs: Any) -> dict[str, Any]:
    kwargs = dict(kwargs)
    kwargs["publish"] = True
    return api_import_curriculum(**kwargs)


def api_archive_curriculum(package_id: str) -> dict[str, Any]:
    return archive_package(package_id)


def api_rollback_version(package_id: str, version_id: str) -> dict[str, Any]:
    return rollback(package_id, version_id)


def api_search_curriculum(query: str = "", **kwargs: Any) -> dict[str, Any]:
    return search_index(
        query,
        board=str(kwargs.get("board") or ""),
        subject=str(kwargs.get("subject") or ""),
        grade=str(kwargs.get("grade") or ""),
        limit=int(kwargs.get("limit") or 25),
    )


def api_compare_curricula(left_board: str, right_board: str) -> dict[str, Any]:
    return cross_board_compare(left_board, right_board)


def api_retrieve_metadata(job_id: str = "", package_id: str = "") -> dict[str, Any]:
    if job_id:
        job = load_job(job_id)
        if not job:
            return {"ok": False, "error": "job_not_found"}
        return {"ok": True, "job": job, "metadata": ((job.get("artifacts") or {}).get("normalize") or {})}
    if package_id:
        return {"ok": True, "versions": version_history(package_id)}
    return {"ok": False, "error": "job_id_or_package_id_required"}


def api_retrieve_package(package_id: str) -> dict[str, Any]:
    from engines.universal_curriculum_framework.curriculum_registry import load_package

    doc = load_package(package_id)
    if not doc:
        return {"ok": False, "error": "not_found"}
    return {"ok": True, "package": doc, "schema": "ucf/1.0"}


def api_get_import_status(job_id: str = "") -> dict[str, Any]:
    if job_id:
        job = load_job(job_id)
        return {"ok": bool(job), "job": job}
    return {"ok": True, "jobs": list_jobs(30), "queue": queue_status()}


def api_dashboard() -> dict[str, Any]:
    return admin_dashboard()


def api_enqueue(**kwargs: Any) -> dict[str, Any]:
    return enqueue(kwargs)


def api_process_queue(**kwargs: Any) -> dict[str, Any]:
    return process_queue(max_jobs=int(kwargs.get("max_jobs") or 3), parallel=bool(kwargs.get("parallel")))


def api_resume(job_id: str, **kwargs: Any) -> dict[str, Any]:
    return resume_job(job_id, **kwargs)


def api_ingest_indian_boards(*, via_cmif: bool = True, publish: bool = True) -> dict[str, Any]:
    """
    Phase 3 content acquisition — ICSE, ISC, Kerala SCERT, NIOS pilots.

    Prefer CMIF mandatory pipeline; falls back to CEF publish-only if via_cmif=False.
    """
    from engines.curriculum_expansion_framework.seeds_indian_boards import seed_indian_boards_packages

    results = []
    if via_cmif:
        for cid, payload in seed_indian_boards_packages():
            results.append(
                run_migration(
                    board=cid,
                    inline=payload,
                    source_url=f"cmif://phase3/{cid}",
                    publisher=str(payload.get("programme") or cid),
                    publish=publish,
                    role="system",
                    lazy_index=True,
                    source_type="inline_json",
                )
            )
        return {
            "ok": all(r.get("ok") for r in results),
            "phase": 3,
            "boards": ["icse", "isc", "kerala_scert", "nios"],
            "via": "cmif",
            "results": results,
            "policy": {"pilot_not_full_corpus": True, "engines_consume_ucf_only": True},
        }

    from engines.curriculum_expansion_framework.service import api_seed_indian_boards

    out = api_seed_indian_boards()
    out["via"] = "cef"
    out["phase"] = 3
    return out


def api_ingest_international(*, via_cmif: bool = True, publish: bool = True) -> dict[str, Any]:
    """
    Phase 4 content acquisition — Cambridge + IB programme pilots.
    """
    from engines.curriculum_expansion_framework.seeds_international import seed_international_packages

    packages = seed_international_packages()
    boards = [cid for cid, _ in packages]
    results = []
    if via_cmif:
        for cid, payload in packages:
            results.append(
                run_migration(
                    board=cid,
                    inline=payload,
                    source_url=f"cmif://phase4/{cid}",
                    publisher=str(payload.get("programme") or cid),
                    publish=publish,
                    role="system",
                    lazy_index=True,
                    source_type="inline_json",
                )
            )
        return {
            "ok": all(r.get("ok") for r in results),
            "phase": 4,
            "boards": boards,
            "families": ["cambridge", "ib"],
            "via": "cmif",
            "results": results,
            "policy": {"pilot_not_full_corpus": True, "engines_consume_ucf_only": True},
        }

    from engines.curriculum_expansion_framework.service import api_seed_international

    out = api_seed_international()
    out["via"] = "cef"
    out["phase"] = 4
    return out


def api_ingest_higher_ed(*, via_cmif: bool = True, publish: bool = True) -> dict[str, Any]:
    """
    Phase 5 content acquisition — university curricula + professional learning frameworks.
    """
    from engines.curriculum_expansion_framework.seeds_higher_ed import seed_higher_ed_packages

    packages = seed_higher_ed_packages()
    boards = [cid for cid, _ in packages]
    results = []
    if via_cmif:
        for cid, payload in packages:
            results.append(
                run_migration(
                    board=cid,
                    inline=payload,
                    source_url=f"cmif://phase5/{cid}",
                    publisher=str(payload.get("programme") or cid),
                    publish=publish,
                    role="system",
                    lazy_index=True,
                    source_type="inline_json",
                )
            )
        return {
            "ok": all(r.get("ok") for r in results),
            "phase": 5,
            "boards": boards,
            "families": ["higher_ed", "professional"],
            "via": "cmif",
            "results": results,
            "policy": {"pilot_not_full_corpus": True, "engines_consume_ucf_only": True},
        }

    from engines.curriculum_expansion_framework.service import api_seed_higher_ed

    out = api_seed_higher_ed()
    out["via"] = "cef"
    out["phase"] = 5
    return out
