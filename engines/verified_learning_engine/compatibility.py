"""Compatibility projections between legacy VLP/readers and v3 contracts."""

from __future__ import annotations

from typing import Any


def adaptations_for_legacy_renderer(
    adaptations: dict[str, Any] | None,
) -> dict[str, Any]:
    """Preserve the nine public keys and existing renderer payload shapes."""
    source = adaptations or {}
    output = dict(source)
    for key in (
        "vocabulary",
        "standard",
        "ld",
        "ell",
        "visual",
        "auditory",
        "teacher",
        "parent",
        "worksheet",
    ):
        output.setdefault(key, {})
    output.setdefault("_meta", {})
    output["_meta"].setdefault("schema_version", "3.0.0")
    return output


def vlp_to_v3(package: dict[str, Any] | None) -> dict[str, Any]:
    """Read VLP v1/v2 packages without inventing curriculum identity."""
    package = dict(package or {})
    if str(package.get("schema_version") or "").startswith("3."):
        return package
    metadata = package.get("lesson_metadata") or {}
    legacy_curriculum = package.get("curriculum") or {}
    citations = legacy_curriculum.get("citations") or []
    package["schema_version"] = "3.0.0"
    package.setdefault(
        "source",
        {
            "schema_version": "legacy",
            "source_id": metadata.get("source_id"),
            "status": "readable" if metadata.get("source_chars") else "unknown",
            "blocks": [],
        },
    )
    package.setdefault(
        "curriculum_resolution",
        {
            "status": "recognized" if citations else "unknown",
            "curriculum": metadata.get("board") if citations else None,
            "confidence": 0.5 if citations else 0.0,
            "provenance": "legacy_package",
        },
    )
    package.setdefault("grounding_mode", "curriculum_enriched" if citations else "uploaded_source")
    package.setdefault(
        "lifecycle_state",
        "quarantined"
        if (package.get("qa_report") or {}).get("publish_blocked")
        else "review_draft",
    )
    package["legacy_schema_version"] = "1.x"
    return package
