"""Shared accessibility recommendation builders — AIE owns application."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from engines.subject_intelligence_core.utilities import reading_band


def build_accessibility_guidance(
    recommendations: Sequence[Mapping[str, Any]],
    uli: Any | None = None,
    *,
    attach_reading_band_to: str | None = "cognitive_load_reduction",
) -> list[dict[str, Any]]:
    """
    Normalize pack accessibility recommendation rows.

    Optionally attaches ULI reading band onto a named recommendation id.
    """
    band = reading_band(uli) if uli is not None else None
    out: list[dict[str, Any]] = []
    for row in recommendations:
        item = dict(row)
        if attach_reading_band_to and item.get("recommendation") == attach_reading_band_to:
            item["reading_band"] = band
        out.append(item)
    return out
