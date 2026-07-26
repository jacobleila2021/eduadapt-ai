"""Accounting intelligence metadata — worked-example scaffolds; no answer leak."""

from __future__ import annotations

from typing import Any

from engines.commerce_economics_intelligence._focus import build_focus_metadata

ACCOUNTING_FOCI: tuple[dict[str, str], ...] = (
    {"id": "accounting_principles", "label": "Accounting principles"},
    {"id": "journal_entries", "label": "Journal entries"},
    {"id": "ledger", "label": "Ledger"},
    {"id": "trial_balance", "label": "Trial balance"},
    {"id": "cash_book", "label": "Cash book"},
    {"id": "financial_statements", "label": "Financial statements"},
    {"id": "ratio_analysis", "label": "Ratio analysis"},
    {"id": "depreciation", "label": "Depreciation"},
    {"id": "inventory", "label": "Inventory"},
    {"id": "cost_accounting", "label": "Cost accounting"},
    {"id": "auditing_fundamentals", "label": "Auditing fundamentals"},
)


def accounting_metadata(
    text: str,
    domains: list[dict[str, Any]],
    *,
    exam_mode: bool = False,
) -> dict[str, Any]:
    return build_focus_metadata(
        foci_catalogue=ACCOUNTING_FOCI,
        text=text,
        domains=domains,
        domain_keys={"accounting"},
        provenance="commerce_economics_intelligence.accounting",
        default_count=8,
        extra={
            "worked_example_scaffolds": [
                "classify_account",
                "dual_entry_check",
                "post_to_ledger",
                "prepare_trial_balance",
            ],
            "interactive_balance_sheet": True,
            "reveals_assessment_answers": False,
            "exam_mode": exam_mode,
        },
    )
