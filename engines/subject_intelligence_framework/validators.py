"""SIF validators — interface / registry compliance (not ULIQE scoring)."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_framework.interfaces import SubjectIntelligencePack
from engines.subject_intelligence_framework.registry import get_registry

REQUIRED_METHODS = (
    "capabilities",
    "analyse_lesson",
    "build_concept_graph",
    "detect_misconceptions",
    "recommend_visuals",
    "recommend_interactions",
    "build_assessment_hints",
    "build_revision_summary",
    "build_accessibility_guidance",
)


def validate_pack_interface(pack: SubjectIntelligencePack) -> dict[str, Any]:
    missing = [name for name in REQUIRED_METHODS if not callable(getattr(pack, name, None))]
    caps = []
    try:
        caps = pack.capabilities()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "errors": [f"capabilities() failed: {exc}"], "missing_methods": missing}
    return {
        "ok": not missing,
        "subject_key": pack.subject.key,
        "missing_methods": missing,
        "capability_count": len(caps),
        "placeholder": getattr(pack, "version", "").endswith("placeholder")
        or "placeholder" in getattr(pack, "version", ""),
    }


def validate_registry() -> dict[str, Any]:
    registry = get_registry()
    reports = [validate_pack_interface(pack) for pack in registry]
    return {
        "ok": all(r["ok"] for r in reports),
        "pack_count": len(reports),
        "packs": reports,
    }
