"""Commerce intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.commerce_economics_intelligence._focus import build_focus_metadata

COMMERCE_FOCI: tuple[dict[str, str], ...] = (
    {"id": "trade", "label": "Trade"},
    {"id": "wholesale_retail", "label": "Wholesale and retail"},
    {"id": "e_commerce", "label": "E-commerce"},
    {"id": "import_export", "label": "Import and export"},
    {"id": "commercial_documents", "label": "Commercial documents"},
)


def commerce_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=COMMERCE_FOCI,
        text=text,
        domains=domains,
        domain_keys={"commerce"},
        provenance="commerce_economics_intelligence.commerce",
    )
