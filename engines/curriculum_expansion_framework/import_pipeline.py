"""CEF import pipeline — external packages → validate → map → UCF."""

from __future__ import annotations

from typing import Any
import uuid

from engines.curriculum_expansion_framework.mapping import map_to_ucf_payload, mapping_completeness, resolve_ucf_board
from engines.curriculum_expansion_framework.provenance import attach_provenance, build_provenance
from engines.curriculum_expansion_framework.registry import append_import_log, ensure_family_catalogue, upsert_entry
from engines.curriculum_expansion_framework.schemas import CURRICULUM_FAMILIES
from engines.curriculum_expansion_framework.validators import validate_expansion_package
from engines.curriculum_expansion_framework.versioning import snapshot


def import_package(
    curriculum_id: str,
    raw: dict[str, Any] | None = None,
    *,
    dry_run: bool = False,
    publish: bool = False,
    source: str = "manual",
) -> dict[str, Any]:
    """
    Import a curriculum package into UCF via CEF.

    Framework-first: unknown boards rejected; engines never see board-specific structs.
    """
    ensure_family_catalogue()
    curriculum_id = (curriculum_id or "").strip().lower()
    if curriculum_id not in CURRICULUM_FAMILIES:
        return {
            "ok": False,
            "error": "unsupported_curriculum",
            "supported": list(CURRICULUM_FAMILIES.keys()),
        }

    raw = dict(raw or {})
    raw.setdefault("board", resolve_ucf_board(curriculum_id))
    raw.setdefault("subject", raw.get("subject") or "Science")
    raw.setdefault("grade", raw.get("grade") or raw.get("year") or "8")

    cef_report = validate_expansion_package(raw)
    if cef_report.get("reject"):
        append_import_log({"curriculum_id": curriculum_id, "event": "rejected", "errors": cef_report.get("errors")})
        upsert_entry({
            "curriculum_id": curriculum_id,
            "import_status": "failed",
            "validation_status": "failed",
            "publication_status": "rejected",
        })
        return {"ok": False, "validation": cef_report, "persisted": False}

    mapped = map_to_ucf_payload(raw, curriculum_id=curriculum_id)
    if not mapped.get("package_id"):
        mapped["package_id"] = f"cef_{curriculum_id}_{uuid.uuid4().hex[:8]}"

    provenance = build_provenance(
        curriculum_id=curriculum_id,
        source=source,
        importer="cef_import_pipeline",
        package_id=str(mapped.get("package_id") or ""),
        licensing=raw.get("licensing"),
        extra={"completeness": mapping_completeness(raw)},
    )
    mapped = attach_provenance(mapped, provenance)

    snap = snapshot(
        curriculum_id,
        {**raw, **mapped},
        version=str(mapped.get("version") or "1.0.0"),
        status="draft",
        note="import",
    )
    if dry_run:
        append_import_log({"curriculum_id": curriculum_id, "event": "dry_run", "package_id": mapped.get("package_id")})
        return {
            "ok": True,
            "dry_run": True,
            "validation": cef_report,
            "mapped": mapped,
            "snapshot": snap,
            "persisted": False,
        }

    from engines.universal_curriculum_framework.import_pipeline import import_curriculum
    from engines.universal_curriculum_framework.validation import validate_package

    ucf_result = import_curriculum(
        "cie_ontology" if mapped.get("concepts") else resolve_ucf_board(curriculum_id),
        mapped,
        dry_run=False,
    )
    if not ucf_result.get("ok"):
        ucf_result = import_curriculum(resolve_ucf_board(curriculum_id), mapped, dry_run=False)

    ucf_val = (ucf_result.get("validation") or {}) if isinstance(ucf_result.get("validation"), dict) else validate_package(mapped)
    package_id = str(ucf_result.get("package_id") or mapped.get("package_id") or "")

    pub_status = "published" if publish and ucf_result.get("ok") else ("validated" if ucf_result.get("ok") else "draft")
    if publish and ucf_result.get("ok"):
        snapshot(curriculum_id, mapped, version=str(mapped.get("version") or "1.0.0"), status="published", note="publish")

    upsert_entry({
        "curriculum_id": curriculum_id,
        "board_name": CURRICULUM_FAMILIES[curriculum_id].get("programme"),
        "programme": CURRICULUM_FAMILIES[curriculum_id].get("programme"),
        "country": CURRICULUM_FAMILIES[curriculum_id].get("country"),
        "region": CURRICULUM_FAMILIES[curriculum_id].get("region") or "",
        "subjects": list({x for x in [*(raw.get("subjects") or []), raw.get("subject")] if x}),
        "grade_levels": list({x for x in [*(raw.get("grade_levels") or []), str(raw.get("grade"))] if x}),
        "languages": list(raw.get("languages") or ["en"]),
        "licensing": raw.get("licensing") or {"status": "restricted"},
        "import_status": "mapped" if ucf_result.get("ok") else "imported",
        "validation_status": "passed" if cef_report.get("ok") and ucf_result.get("ok") else "warnings",
        "publication_status": pub_status,
        "ucf_board_id": resolve_ucf_board(curriculum_id),
        "ucf_package_ids": [package_id] if package_id else [],
        "family_id": CURRICULUM_FAMILIES[curriculum_id].get("family"),
        "version": str(mapped.get("version") or "1.0.0"),
        "provenance": provenance,
    })
    append_import_log({
        "curriculum_id": curriculum_id,
        "event": "imported",
        "package_id": package_id,
        "ucf_ok": bool(ucf_result.get("ok")),
        "published": publish,
    })

    return {
        "ok": bool(ucf_result.get("ok")),
        "curriculum_id": curriculum_id,
        "package_id": package_id,
        "validation": {"cef": cef_report, "ucf": ucf_val},
        "ucf_result": {k: ucf_result.get(k) for k in ("ok", "package_id", "path", "persisted", "error")},
        "snapshot": snap,
        "publication_status": pub_status,
        "policy": {"engines_consume_ucf_only": True},
    }


def publish_package(curriculum_id: str, package_id: str = "") -> dict[str, Any]:
    """Mark registry entry published after UCF package exists."""
    from engines.curriculum_expansion_framework.registry import get_entry
    from engines.universal_curriculum_framework.curriculum_registry import load_package, save_package

    entry = get_entry(curriculum_id)
    if not entry:
        return {"ok": False, "error": "curriculum_not_found"}
    pid = package_id or (entry.get("ucf_package_ids") or [""])[0]
    if pid and not load_package(pid):
        return {"ok": False, "error": "ucf_package_not_found", "package_id": pid}
    upsert_entry({
        "curriculum_id": curriculum_id,
        "publication_status": "published",
        "validation_status": "passed",
        "import_status": "mapped",
    })
    if pid:
        doc = load_package(pid)
        if doc:
            doc["status"] = "active"
            save_package(doc)
    snapshot(curriculum_id, {"package_id": pid}, status="published", note="publish_api")
    append_import_log({"curriculum_id": curriculum_id, "event": "published", "package_id": pid})
    return {"ok": True, "curriculum_id": curriculum_id, "package_id": pid, "publication_status": "published"}
