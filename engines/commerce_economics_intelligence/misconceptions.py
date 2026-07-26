"""Commerce & economics misconceptions — SICS catalogue detection."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.misconceptions import detect_from_catalogue

COMMERCE_ECONOMICS_MISCONCEPTIONS: tuple[dict[str, Any], ...] = (
    {
        "misconception_id": "ce.debit_always_increase",
        "label": "Debit always means increase",
        "domain": "accounting",
        "patterns": [
            r"debit\s*(always\s*)?(means\s*)?increase",
            r"debit\s*always\s*means\s*increase",
            r"credit\s*(always\s*)?(means\s*)?decrease",
        ],
        "correction": "Debit/credit depend on account type (assets vs liabilities/equity/income). Teach the dual-aspect rule with account classification.",
        "related_concepts": ["journal", "ledger", "accounting_equation"],
    },
    {
        "misconception_id": "ce.profit_equals_cash",
        "label": "Profit equals cash in the bank",
        "domain": "accounting",
        "patterns": [
            r"profit\s*(equals|is\s*the\s*same\s*as)\s*cash",
            r"net\s*profit\s*(is\s*)?(always\s*)?cash",
        ],
        "correction": "Accrual profit differs from cash flow; reconcile via working capital and non-cash items.",
        "related_concepts": ["financial_statements", "cash_flow", "accrual"],
    },
    {
        "misconception_id": "ce.price_only_seller",
        "label": "Prices are set only by sellers",
        "domain": "economics",
        "patterns": [
            r"sellers?\s*(alone\s*)?(set|decide)\s*prices?",
            r"demand\s*(does\s*not|doesn't)\s*affect\s*price",
        ],
        "correction": "In market models, price emerges from interaction of supply and demand (with institutions/rules).",
        "related_concepts": ["supply", "demand", "markets"],
    },
    {
        "misconception_id": "ce.inflation_always_bad",
        "label": "All inflation is always harmful",
        "domain": "economics",
        "patterns": [
            r"inflation\s*(is\s*)?(always|never)\s*(bad|harmful|good)",
            r"any\s*inflation\s*(destroys|ruins)\s*(the\s*)?economy",
        ],
        "correction": "Distinguish moderate vs high/hyperinflation; discuss causes, distributional effects, and policy trade-offs.",
        "related_concepts": ["inflation", "monetary_policy", "purchasing_power"],
    },
    {
        "misconception_id": "ce.investment_guaranteed",
        "label": "Investments always grow / are risk-free",
        "domain": "finance",
        "patterns": [
            r"investments?\s*(always|guaranteed?\s*to)\s*(grow|profit|return)",
            r"stock\s*market\s*(is\s*)?(risk[\s-]*free|never\s*loses)",
        ],
        "correction": "Return and risk trade off; diversify and match horizon; no guaranteed market returns in teaching models.",
        "related_concepts": ["risk", "return", "diversification"],
    },
    {
        "misconception_id": "ce.idea_is_business",
        "label": "A good idea alone is a successful business",
        "domain": "entrepreneurship",
        "patterns": [
            r"(good\s*)?idea\s*(alone\s*)?(is|equals)\s*(a\s*)?(successful\s*)?business",
            r"no\s*need\s*(for\s*)?(customers|validation|plan)",
        ],
        "correction": "Validate customers, model revenue/costs, and iterate; ideas need execution and market fit.",
        "related_concepts": ["market_validation", "business_canvas", "revenue_models"],
    },
    {
        "misconception_id": "ce.marketing_only_ads",
        "label": "Marketing is only advertising",
        "domain": "marketing",
        "patterns": [
            r"marketing\s*(is\s*)?(only|just)\s*(ads?|advertising)",
            r"marketing\s*=\s*promotion",
        ],
        "correction": "Marketing includes product, price, place, promotion, research, and customer value—not ads alone.",
        "related_concepts": ["marketing_mix", "branding", "market_research"],
    },
    {
        "misconception_id": "ce.management_only_boss",
        "label": "Management is only giving orders",
        "domain": "management",
        "patterns": [
            r"management\s*(is\s*)?(only|just)\s*(giving\s*)?orders",
            r"managers?\s*(only\s*)?tell\s*people\s*what\s*to\s*do",
        ],
        "correction": "Management includes planning, organising, leading, controlling, and enabling people and processes.",
        "related_concepts": ["planning", "leadership", "decision_making"],
    },
)


def detect_commerce_economics_misconceptions(text: str, *, limit: int = 12) -> list[dict[str, Any]]:
    return detect_from_catalogue(
        COMMERCE_ECONOMICS_MISCONCEPTIONS,
        text,
        provenance="commerce_economics_intelligence.misconceptions",
        limit=limit,
    )
