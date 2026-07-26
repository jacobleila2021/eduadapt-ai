"""Taxation intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.commerce_economics_intelligence._focus import build_focus_metadata

TAXATION_FOCI: tuple[dict[str, str], ...] = (
    {"id": "direct_tax", "label": "Direct tax"},
    {"id": "indirect_tax", "label": "Indirect tax"},
    {"id": "gst", "label": "GST"},
    {"id": "income_tax", "label": "Income tax"},
    {"id": "tax_compliance", "label": "Tax compliance"},
)


def taxation_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=TAXATION_FOCI,
        text=text,
        domains=domains,
        domain_keys={"taxation"},
        provenance="commerce_economics_intelligence.taxation",
        default_count=4,
        extra={"invents_tax_advice": False},
    )
