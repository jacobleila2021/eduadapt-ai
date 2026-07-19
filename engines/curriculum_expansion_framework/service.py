"""REST-shaped API facade for Curriculum Expansion Framework."""

from __future__ import annotations

from typing import Any

from engines.curriculum_expansion_framework.dashboards import admin_dashboard
from engines.curriculum_expansion_framework.equivalency import compare_curricula
from engines.curriculum_expansion_framework.import_pipeline import import_package, publish_package
from engines.curriculum_expansion_framework.registry import (
    ensure_family_catalogue,
    get_entry,
    list_curricula,
    list_supported_boards,
)
from engines.curriculum_expansion_framework.search import search_expansion
from engines.curriculum_expansion_framework.seeds import seed_priority_packages
from engines.curriculum_expansion_framework.validators import validate_expansion_package
from engines.curriculum_expansion_framework.versioning import compare_versions, rollback, version_history


def api_list_supported_boards() -> dict[str, Any]:
    return {"ok": True, "boards": list_supported_boards()}


def api_import_curriculum_package(curriculum_id: str, payload: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    return import_package(
        curriculum_id,
        payload,
        dry_run=bool(kwargs.get("dry_run")),
        publish=bool(kwargs.get("publish")),
        source=str(kwargs.get("source") or "api"),
    )


def api_validate_package(package: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "validation": validate_expansion_package(package)}


def api_publish_package(curriculum_id: str, package_id: str = "") -> dict[str, Any]:
    return publish_package(curriculum_id, package_id)


def api_retrieve_curriculum_metadata(curriculum_id: str) -> dict[str, Any]:
    ensure_family_catalogue()
    entry = get_entry(curriculum_id)
    if not entry:
        return {"ok": False, "error": "not_found"}
    return {"ok": True, "curriculum": entry}


def api_search_curriculum(query: str, **kwargs: Any) -> dict[str, Any]:
    return search_expansion(
        query,
        board=str(kwargs.get("board") or ""),
        subject=str(kwargs.get("subject") or ""),
        grade=str(kwargs.get("grade") or ""),
        competency=str(kwargs.get("competency") or ""),
        limit=int(kwargs.get("limit") or 25),
        locale=str(kwargs.get("locale") or "en-IN"),
    )


def api_compare_curricula(**kwargs: Any) -> dict[str, Any]:
    return compare_curricula(
        left_package_id=str(kwargs.get("left_package_id") or ""),
        right_package_id=str(kwargs.get("right_package_id") or ""),
        left_board=str(kwargs.get("left_board") or ""),
        right_board=str(kwargs.get("right_board") or ""),
        threshold=float(kwargs.get("threshold") or 0.15),
    )


def api_version_history(curriculum_id: str) -> dict[str, Any]:
    return version_history(curriculum_id)


def api_compare_versions(curriculum_id: str, snapshot_a: str, snapshot_b: str) -> dict[str, Any]:
    return compare_versions(curriculum_id, snapshot_a, snapshot_b)


def api_rollback(curriculum_id: str, snapshot_id: str) -> dict[str, Any]:
    return rollback(curriculum_id, snapshot_id)


def api_dashboard() -> dict[str, Any]:
    return admin_dashboard()


def api_list_curricula(**kwargs: Any) -> dict[str, Any]:
    return {
        "ok": True,
        "curricula": list_curricula(
            family=str(kwargs.get("family") or ""),
            publication_status=str(kwargs.get("publication_status") or ""),
            country=str(kwargs.get("country") or ""),
        ),
    }


def api_seed_priority() -> dict[str, Any]:
    """Import NCERT + CBSE seeds (incremental step 1)."""
    results = []
    for cid, payload in seed_priority_packages():
        results.append(import_package(cid, payload, publish=True, source="cef_seed"))
    return {"ok": all(r.get("ok") for r in results), "results": results}


def api_seed_indian_boards() -> dict[str, Any]:
    """Import ICSE, ISC, Kerala SCERT, NIOS pilots (incremental Phase 3)."""
    from engines.curriculum_expansion_framework.seeds_indian_boards import seed_indian_boards_packages

    results = []
    for cid, payload in seed_indian_boards_packages():
        results.append(import_package(cid, payload, publish=True, source="cef_phase3_indian_boards"))
    return {
        "ok": all(r.get("ok") for r in results),
        "phase": "indian_boards",
        "boards": ["icse", "isc", "kerala_scert", "nios"],
        "results": results,
        "policy": {"engines_consume_ucf_only": True, "pilot_packages_not_full_corpus": True},
    }


def api_seed_international() -> dict[str, Any]:
    """Import Cambridge + IB programme pilots (incremental Phase 4)."""
    from engines.curriculum_expansion_framework.seeds_international import seed_international_packages

    results = []
    for cid, payload in seed_international_packages():
        results.append(import_package(cid, payload, publish=True, source="cef_phase4_international"))
    boards = [cid for cid, _ in seed_international_packages()]
    return {
        "ok": all(r.get("ok") for r in results),
        "phase": "international",
        "boards": boards,
        "families": ["cambridge", "ib"],
        "results": results,
        "policy": {"engines_consume_ucf_only": True, "pilot_packages_not_full_corpus": True},
    }


def api_seed_higher_ed() -> dict[str, Any]:
    """Import university + professional learning pilots (incremental Phase 5)."""
    from engines.curriculum_expansion_framework.seeds_higher_ed import seed_higher_ed_packages

    packages = seed_higher_ed_packages()
    results = []
    for cid, payload in packages:
        results.append(import_package(cid, payload, publish=True, source="cef_phase5_higher_ed"))
    return {
        "ok": all(r.get("ok") for r in results),
        "phase": "higher_ed_professional",
        "boards": [cid for cid, _ in packages],
        "families": ["higher_ed", "professional"],
        "results": results,
        "policy": {"engines_consume_ucf_only": True, "pilot_packages_not_full_corpus": True},
    }
