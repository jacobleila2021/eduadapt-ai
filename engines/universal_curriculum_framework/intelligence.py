"""UCF intelligence — ensure package available & expose consume projections."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework import adapters
from engines.universal_curriculum_framework.board_registry import list_boards
from engines.universal_curriculum_framework.curriculum_model import catalogue, get_curriculum_model
from engines.universal_curriculum_framework.curriculum_registry import (
    list_packages,
    load_package,
)
from engines.universal_curriculum_framework.import_pipeline import import_curriculum


def ensure_pilot_ucf() -> dict[str, Any]:
    """Import pilot CIE ontology into UCF if registry empty."""
    if list_packages():
        return {"ok": True, "already_present": True, "packages": list_packages()}
    result = import_curriculum("cie_ontology", {"board": "cbse", "grade": "8", "subject": "Science"})
    return result


def analyze_ucf_context(context: dict[str, Any]) -> dict[str, Any]:
    ensure = ensure_pilot_ucf()
    package_id = str(context.get("ucf_package_id") or context.get("curriculum_id") or "")
    scope = {
        "board": str(context.get("board") or "").strip().lower(),
        "grade": str(context.get("grade") or context.get("grade_level") or "").strip().lower(),
        "subject": str(context.get("subject") or "").strip().lower(),
    }
    if not package_id:
        candidates = sorted(
            list_packages(),
            key=lambda row: str(row.get("updated_at") or ""),
            reverse=True,
        )
        for row in candidates:
            doc = load_package(str(row.get("package_id") or "")) or {}
            board = str((doc.get("board") or {}).get("board_id") or "").lower()
            structure = doc.get("structure") or {}
            grade = str(structure.get("grade") or "").lower()
            subject = str(structure.get("subject") or "").lower()
            if scope["board"] and scope["board"] not in {
                board,
                str((doc.get("board") or {}).get("board_name") or "").lower(),
            }:
                continue
            if scope["grade"] and scope["grade"] != grade:
                continue
            if scope["subject"] and scope["subject"] != subject:
                continue
            package_id = str(row.get("package_id") or "")
            break
    model = get_curriculum_model(package_id) if package_id else {"ok": False}
    return {
        "system": "UCF",
        "schema": "ucf/1.0",
        "ensure": {"ok": ensure.get("ok"), "package_id": ensure.get("package_id")},
        "package_id": package_id,
        "catalogue": catalogue(),
        "boards": list_boards(),
        "model_ok": bool(model.get("ok")),
        "scope_matched": bool(package_id),
        "requested_scope": scope,
        "cie_projection": model.get("cie_projection") if model.get("ok") else {},
        "adapters": {
            "cie": adapters.for_cie(package_id),
            "ame": adapters.for_ame(package_id),
            "ale": adapters.for_ale(package_id),
            "aie": adapters.for_aie(package_id),
            "atie": adapters.for_atie(package_id),
            "vmle": adapters.for_vmle(package_id),
            "alcis": adapters.for_alcis(package_id),
            "lmas": adapters.for_lmas(package_id),
            "laie": adapters.for_laie(package_id),
        },
        "policy": {
            "single_internal_representation": True,
            "engines_consume_ucf_not_board_structs": True,
            "official_questions_never_replaced_by_ai": True,
            "board_expansion_via_importers_only": True,
        },
    }
