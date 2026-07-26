"""Business studies intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.commerce_economics_intelligence._focus import build_focus_metadata

BUSINESS_FOCI: tuple[dict[str, str], ...] = (
    {"id": "business_organisations", "label": "Business organisations"},
    {"id": "management_principles", "label": "Management principles"},
    {"id": "leadership", "label": "Leadership"},
    {"id": "human_resources", "label": "Human resources"},
    {"id": "operations", "label": "Operations"},
    {"id": "business_ethics", "label": "Business ethics"},
    {"id": "corporate_governance", "label": "Corporate governance"},
    {"id": "business_environment", "label": "Business environment"},
    {"id": "decision_making", "label": "Decision making"},
)


def business_studies_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=BUSINESS_FOCI,
        text=text,
        domains=domains,
        domain_keys={"business_studies"},
        provenance="commerce_economics_intelligence.business_studies",
        default_count=7,
        extra={
            "decision_tree_viewer": True,
            "business_process_flowcharts": True,
        },
    )
