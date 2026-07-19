"""Provenance tracking for imported curriculum packages."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_provenance(
    *,
    curriculum_id: str,
    source: str,
    importer: str,
    package_id: str = "",
    licensing: dict[str, Any] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "curriculum_id": curriculum_id,
        "source": source,
        "importer": importer,
        "package_id": package_id,
        "imported_at": _now(),
        "licensing": licensing or {"status": "restricted"},
        "chain": ["external_source", "cef", "ucf", "engines"],
        "policy": {
            "engines_consume_ucf_only": True,
            "no_board_branches_in_engines": True,
        },
        **(extra or {}),
    }


def attach_provenance(package: dict[str, Any], provenance: dict[str, Any]) -> dict[str, Any]:
    out = dict(package)
    out["provenance"] = {**(out.get("provenance") or {}), **provenance}
    return out
