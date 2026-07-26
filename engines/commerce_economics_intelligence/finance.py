"""Finance intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.commerce_economics_intelligence._focus import build_focus_metadata

FINANCE_FOCI: tuple[dict[str, str], ...] = (
    {"id": "banking", "label": "Banking"},
    {"id": "investment", "label": "Investment"},
    {"id": "insurance", "label": "Insurance"},
    {"id": "financial_markets", "label": "Financial markets"},
    {"id": "budgeting", "label": "Budgeting"},
    {"id": "personal_finance", "label": "Personal finance"},
    {"id": "capital_markets", "label": "Capital markets"},
    {"id": "risk_management", "label": "Risk management"},
    {"id": "corporate_finance", "label": "Corporate finance"},
)


def finance_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=FINANCE_FOCI,
        text=text,
        domains=domains,
        domain_keys={"finance"},
        provenance="commerce_economics_intelligence.finance",
        default_count=7,
        extra={
            "investment_timelines": True,
            "financial_dashboard": True,
            "invents_returns": False,
        },
    )
