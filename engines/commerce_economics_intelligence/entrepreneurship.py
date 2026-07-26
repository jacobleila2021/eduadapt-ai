"""Entrepreneurship intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.commerce_economics_intelligence._focus import build_focus_metadata

ENTREPRENEURSHIP_FOCI: tuple[dict[str, str], ...] = (
    {"id": "innovation", "label": "Innovation"},
    {"id": "start_ups", "label": "Start-ups"},
    {"id": "business_planning", "label": "Business planning"},
    {"id": "market_validation", "label": "Market validation"},
    {"id": "revenue_models", "label": "Revenue models"},
    {"id": "business_canvas", "label": "Business canvas"},
    {"id": "scaling", "label": "Scaling"},
    {"id": "social_entrepreneurship", "label": "Social entrepreneurship"},
)


def entrepreneurship_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=ENTREPRENEURSHIP_FOCI,
        text=text,
        domains=domains,
        domain_keys={"entrepreneurship"},
        provenance="commerce_economics_intelligence.entrepreneurship",
        default_count=6,
        extra={
            "business_model_canvas": True,
            "invents_business_plans": False,
        },
    )
