"""Curriculum model facade — unified view for engines."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework.board_registry import list_boards, supported_board_names
from engines.universal_curriculum_framework.competency import list_competencies
from engines.universal_curriculum_framework.curriculum_registry import list_packages, load_package
from engines.universal_curriculum_framework.mapping import ucf_package_to_cie_payload
from engines.universal_curriculum_framework.prerequisites import build_dependency_graph


def get_curriculum_model(package_id: str) -> dict[str, Any]:
    pkg = load_package(package_id)
    if not pkg:
        return {"ok": False, "error": "not_found"}
    return {
        "ok": True,
        "package": pkg,
        "cie_projection": ucf_package_to_cie_payload(pkg),
        "competencies": list_competencies(pkg),
        "knowledge_graph": build_dependency_graph(pkg),
        "boards_supported": supported_board_names(),
    }


def catalogue() -> dict[str, Any]:
    return {
        "boards": list_boards(),
        "packages": list_packages(),
        "schema": "ucf/1.0",
    }
