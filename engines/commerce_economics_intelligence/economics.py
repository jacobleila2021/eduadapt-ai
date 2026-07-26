"""Economics intelligence metadata — concept relationships and cause–effect."""

from __future__ import annotations

from typing import Any

from engines.commerce_economics_intelligence._focus import build_focus_metadata

ECONOMICS_FOCI: tuple[dict[str, str], ...] = (
    {"id": "demand", "label": "Demand"},
    {"id": "supply", "label": "Supply"},
    {"id": "elasticity", "label": "Elasticity"},
    {"id": "market_structures", "label": "Market structures"},
    {"id": "national_income", "label": "National income"},
    {"id": "inflation", "label": "Inflation"},
    {"id": "employment", "label": "Employment"},
    {"id": "fiscal_policy", "label": "Fiscal policy"},
    {"id": "monetary_policy", "label": "Monetary policy"},
    {"id": "international_trade", "label": "International trade"},
    {"id": "development_economics", "label": "Development economics"},
)


def economics_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=ECONOMICS_FOCI,
        text=text,
        domains=domains,
        domain_keys={"economics"},
        provenance="commerce_economics_intelligence.economics",
        default_count=8,
        extra={
            "cause_effect_mappings": [
                {"from": "demand_shift", "to": "equilibrium_price_quantity"},
                {"from": "money_supply", "to": "inflation_pressure"},
                {"from": "fiscal_stimulus", "to": "aggregate_demand"},
            ],
            "concept_relationships": True,
            "economic_graph_explorer": True,
        },
    )
