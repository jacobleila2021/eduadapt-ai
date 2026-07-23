"""EATS revise gate — call existing PQLE revise API (read-only consumer), then re-evaluate."""

from __future__ import annotations

from typing import Any, Mapping

from eats.constants import MAX_REVISE_ATTEMPTS, PUBLISHER_READY


def attempt_revise(
    adaptations: dict[str, Any],
    *,
    clg: Mapping[str, Any] | None = None,
    max_passes: int = MAX_REVISE_ATTEMPTS,
) -> dict[str, Any]:
    """Invoke PQLE revise loop without modifying LCE/PQLE source."""
    out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in adaptations.items()}
    meta: dict[str, Any] = {"used_pqle_revise": False, "error": ""}
    try:
        from engines.lesson_composition_engine.revise import apply_publisher_quality_excellence

        result = apply_publisher_quality_excellence(out, clg=clg or {}, max_passes=max_passes)
        revised = result.get("adaptations") or out
        out = {k: (dict(v) if isinstance(v, dict) else v) for k, v in revised.items()}
        if isinstance(adaptations.get("_meta"), dict):
            merged_meta = dict(adaptations["_meta"])
            if isinstance(out.get("_meta"), dict):
                merged_meta.update(out["_meta"])
            out["_meta"] = merged_meta
        meta["used_pqle_revise"] = True
        meta["pqle"] = {
            "publication_ready": result.get("publication_ready"),
            "reject_rendering": result.get("reject_rendering"),
            "pqi": result.get("pqi"),
            "threshold": result.get("threshold") or PUBLISHER_READY,
        }
    except Exception as exc:
        meta["error"] = str(exc)[:240]
    return {"adaptations": out, "revise_meta": meta}
