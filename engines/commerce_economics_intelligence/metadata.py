"""CEIP metadata envelope."""

from __future__ import annotations

from typing import Any, Mapping

from engines.subject_intelligence_core.metadata import pack_metadata_envelope


def build_pack_metadata(
    *,
    version: str,
    domains: list[dict[str, Any]],
    exam_mode: bool,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return pack_metadata_envelope(
        pack="commerce_economics_intelligence",
        version=version,
        domains=domains,
        exam_mode=exam_mode,
        extra=extra,
    )
