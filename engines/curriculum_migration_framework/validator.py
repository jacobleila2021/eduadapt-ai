"""CMIF validation — reject incomplete packages before UCF publish."""

from __future__ import annotations

from typing import Any

from engines.curriculum_expansion_framework.validators import validate_expansion_package


def validate_package(raw: dict[str, Any], *, provenance: dict[str, Any] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    # Hierarchy / IDs
    topics = raw.get("topics") or raw.get("concepts") or []
    ids: list[str] = []
    for t in topics:
        tid = t if isinstance(t, str) else str(t.get("id") or t.get("topic_id") or "")
        if not tid:
            errors.append("missing_topic_id")
        elif tid in ids:
            errors.append(f"duplicate_id:{tid}")
        else:
            ids.append(tid)

    chapters = raw.get("chapters") or []
    if chapters and not topics:
        errors.append("missing_chapters_content")

    # Reuse CEF expansion validator
    cef = validate_expansion_package(raw)
    errors.extend(cef.get("errors") or [])
    warnings.extend(cef.get("warnings") or [])

    if provenance is not None and not provenance.get("source_hash"):
        warnings.append("source_hash_missing")
    if provenance is not None and not (provenance.get("source_url") or provenance.get("source_type")):
        errors.append("source_provenance_incomplete")

    # Formula rendering integrity
    for f in raw.get("formulae") or raw.get("formulas") or raw.get("equations") or []:
        if isinstance(f, dict) and not (f.get("latex") or f.get("formula") or f.get("expression")):
            errors.append("formula_rendering_failed")

    for fig in raw.get("figures") or raw.get("diagrams") or []:
        if isinstance(fig, dict) and not (fig.get("alt_text") or fig.get("path") or fig.get("diagram_id")):
            warnings.append("diagram_integrity_weak")

    ok = not errors
    quality = max(0.0, min(1.0, 1.0 - 0.12 * len(errors) - 0.03 * len(warnings)))
    return {
        "ok": ok,
        "reject": not ok,
        "errors": errors,
        "warnings": warnings,
        "quality_score": round(quality, 3),
        "cef": cef,
        "version_integrity": True,
    }
