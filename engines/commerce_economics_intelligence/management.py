"""Management intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.commerce_economics_intelligence._focus import build_focus_metadata

MANAGEMENT_FOCI: tuple[dict[str, str], ...] = (
    {"id": "planning", "label": "Planning"},
    {"id": "organising", "label": "Organising"},
    {"id": "staffing", "label": "Staffing"},
    {"id": "directing", "label": "Directing"},
    {"id": "controlling", "label": "Controlling"},
    {"id": "motivation", "label": "Motivation"},
)


def management_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=MANAGEMENT_FOCI,
        text=text,
        domains=domains,
        domain_keys={"management", "business_studies"},
        provenance="commerce_economics_intelligence.management",
    )
