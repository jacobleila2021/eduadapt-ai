"""Marketing intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.commerce_economics_intelligence._focus import build_focus_metadata

MARKETING_FOCI: tuple[dict[str, str], ...] = (
    {"id": "consumer_behaviour", "label": "Consumer behaviour"},
    {"id": "branding", "label": "Branding"},
    {"id": "product_lifecycle", "label": "Product lifecycle"},
    {"id": "promotion", "label": "Promotion"},
    {"id": "pricing", "label": "Pricing"},
    {"id": "distribution", "label": "Distribution"},
    {"id": "digital_marketing", "label": "Digital marketing"},
    {"id": "market_research", "label": "Market research"},
)


def marketing_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=MARKETING_FOCI,
        text=text,
        domains=domains,
        domain_keys={"marketing"},
        provenance="commerce_economics_intelligence.marketing",
    )
