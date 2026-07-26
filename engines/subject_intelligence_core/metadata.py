"""Pack analysis metadata envelope helpers."""

from __future__ import annotations

from typing import Any, Mapping


def pack_metadata_envelope(
    *,
    pack: str,
    version: str,
    domains: list[dict[str, Any]],
    exam_mode: bool,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    base: dict[str, Any] = {
        "pack": pack,
        "version": version,
        "domains": domains,
        "exam_mode": exam_mode,
        "mutates_curriculum": False,
    }
    if extra:
        base.update(dict(extra))
    return base


def laboratory_metadata_template(
    *,
    lab_id: str,
    provenance: str,
    aim: str | None = None,
    frameworks: list[str] | None = None,
    safety: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "lab_id": lab_id,
        "aim": aim,
        "frameworks": list(frameworks or ["inquiry", "cer"]),
        "safety_guidance": list(safety or []),
        "source_bound": True,
        "provenance": provenance,
    }
