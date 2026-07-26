"""Financial literacy intelligence metadata."""

from __future__ import annotations

from typing import Any

from engines.commerce_economics_intelligence._focus import build_focus_metadata

FINANCIAL_LITERACY_FOCI: tuple[dict[str, str], ...] = (
    {"id": "saving", "label": "Saving"},
    {"id": "budgeting", "label": "Budgeting"},
    {"id": "credit_debt", "label": "Credit and debt"},
    {"id": "compound_interest", "label": "Compound interest"},
    {"id": "money_management", "label": "Money management"},
)


def financial_literacy_metadata(text: str, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=FINANCIAL_LITERACY_FOCI,
        text=text,
        domains=domains,
        domain_keys={"financial_literacy", "finance"},
        provenance="commerce_economics_intelligence.financial_literacy",
    )
