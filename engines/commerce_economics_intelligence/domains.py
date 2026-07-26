"""Commerce & economics domain detection."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.taxonomy import (
    concept_graph_from_uli as _concept_graph,
    detect_domains as _detect_domains,
    prerequisite_hints as _prerequisite_hints,
)

DOMAIN_MARKERS: dict[str, tuple[str, ...]] = {
    "accounting": (
        "accounting",
        "accountancy",
        "journal",
        "ledger",
        "trial balance",
        "cash book",
        "financial statement",
        "balance sheet",
        "depreciation",
        "inventory",
        "cost accounting",
        "audit",
        "ratio analysis",
    ),
    "economics": (
        "economics",
        "demand",
        "supply",
        "elasticity",
        "market structure",
        "national income",
        "inflation",
        "fiscal policy",
        "monetary policy",
        "international trade",
        "gdp",
        "employment",
        "development economics",
    ),
    "business_studies": (
        "business studies",
        "business organisation",
        "business organization",
        "management principle",
        "leadership",
        "human resources",
        "operations",
        "business ethics",
        "corporate governance",
        "business environment",
        "decision making",
    ),
    "finance": (
        "finance",
        "banking",
        "investment",
        "insurance",
        "financial market",
        "budgeting",
        "capital market",
        "risk management",
        "corporate finance",
        "personal finance",
    ),
    "entrepreneurship": (
        "entrepreneurship",
        "entrepreneur",
        "start-up",
        "startup",
        "innovation",
        "business planning",
        "market validation",
        "revenue model",
        "business canvas",
        "business model canvas",
        "scaling",
        "social entrepreneurship",
    ),
    "management": (
        "management",
        "planning",
        "organising",
        "organizing",
        "controlling",
        "staffing",
        "motivation",
        "organisational structure",
    ),
    "marketing": (
        "marketing",
        "consumer behaviour",
        "consumer behavior",
        "branding",
        "product lifecycle",
        "promotion",
        "pricing",
        "distribution",
        "digital marketing",
        "market research",
    ),
    "taxation": (
        "taxation",
        "tax",
        "gst",
        "income tax",
        "indirect tax",
        "direct tax",
        "vat",
        "customs duty",
    ),
    "commerce": (
        "commerce",
        "trade",
        "wholesale",
        "retail",
        "e-commerce",
        "import",
        "export",
        "merchant",
    ),
    "financial_literacy": (
        "financial literacy",
        "saving",
        "budget",
        "compound interest",
        "credit",
        "debt",
        "money management",
    ),
}

PREREQ_EDGES: tuple[tuple[str, str], ...] = (
    ("financial_literacy", "finance"),
    ("accounting", "finance"),
    ("economics", "finance"),
    ("commerce", "business_studies"),
    ("business_studies", "management"),
    ("business_studies", "marketing"),
    ("management", "entrepreneurship"),
    ("marketing", "entrepreneurship"),
    ("finance", "entrepreneurship"),
    ("accounting", "taxation"),
    ("economics", "commerce"),
    ("finance", "taxation"),
)


def detect_domains(text: str) -> list[dict[str, Any]]:
    return _detect_domains(text, DOMAIN_MARKERS)


def prerequisite_hints(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _prerequisite_hints(
        domains,
        PREREQ_EDGES,
        provenance="commerce_economics_intelligence.domain_prereqs",
    )


def concept_graph_from_uli(uli: Any, domains: list[dict[str, Any]]) -> dict[str, Any]:
    return _concept_graph(
        uli,
        domains,
        PREREQ_EDGES,
        domain_node_type="commerce_economics_domain",
        provenance="commerce_economics_intelligence",
    )
