"""CEIP quality signals for ULIQE — additive INFO only."""

from __future__ import annotations

from typing import Any, Mapping

from engines.commerce_economics_intelligence.accounting import accounting_metadata
from engines.commerce_economics_intelligence.business_studies import business_studies_metadata
from engines.commerce_economics_intelligence.domains import detect_domains
from engines.commerce_economics_intelligence.economics import economics_metadata
from engines.commerce_economics_intelligence.entrepreneurship import entrepreneurship_metadata
from engines.commerce_economics_intelligence.finance import finance_metadata
from engines.commerce_economics_intelligence.misconceptions import detect_commerce_economics_misconceptions
from engines.subject_intelligence_core.utilities import envelope_text
from engines.subject_intelligence_core.validation import finding_seed


def _source_text(uli: Any) -> str:
    parts = [envelope_text(uli)]
    try:
        learn = dict(uli.learning_structure())
        for c in learn.get("key_concepts") or []:
            if isinstance(c, Mapping):
                parts.append(str(c.get("concept") or ""))
        for o in learn.get("learning_objectives") or []:
            if isinstance(o, Mapping):
                parts.append(str(o.get("objective") or ""))
            else:
                parts.append(str(o))
    except Exception:  # noqa: BLE001
        pass
    return "\n".join(p for p in parts if p)


def collect_commerce_economics_quality_signals(uli: Any) -> dict[str, Any]:
    text = _source_text(uli)
    domains = detect_domains(text)
    misconceptions = detect_commerce_economics_misconceptions(text)
    accounting = accounting_metadata(text, domains)
    economics = economics_metadata(text, domains)
    finance = finance_metadata(text, domains)
    business = business_studies_metadata(text, domains)
    entrepreneurship = entrepreneurship_metadata(text, domains)

    teaching = {
        "domains_detected": len(domains),
        "accounting_foci": len(accounting.get("foci") or []),
        "economics_foci": len(economics.get("foci") or []),
        "finance_foci": len(finance.get("foci") or []),
        "business_foci": len(business.get("foci") or []),
        "entrepreneurship_foci": len(entrepreneurship.get("foci") or []),
        "misconception_annotations": len(misconceptions),
    }

    findings_seed: list[dict[str, Any]] = []
    if domains:
        findings_seed.append(
            finding_seed(
                "ULIQE.CEIP.000",
                "info",
                f"CEIP signals: {len(domains)} domain(s).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "accounting" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.CEIP.ACCOUNTING",
                "info",
                f"Accounting metadata active ({teaching['accounting_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "economics" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.CEIP.ECONOMICS",
                "info",
                f"Economics metadata active ({teaching['economics_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] in {"finance", "financial_literacy"} for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.CEIP.FINANCE",
                "info",
                f"Finance metadata active ({teaching['finance_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] in {"business_studies", "management", "marketing", "commerce"} for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.CEIP.BUSINESS",
                "info",
                f"Business studies metadata active ({teaching['business_foci']} foci).",
                category="pedagogy",
            )
        )
    if any(d["domain"] == "entrepreneurship" for d in domains):
        findings_seed.append(
            finding_seed(
                "ULIQE.CEIP.ENTREPRENEURSHIP",
                "info",
                f"Entrepreneurship metadata active ({teaching['entrepreneurship_foci']} foci).",
                category="pedagogy",
            )
        )
    if misconceptions:
        findings_seed.append(
            finding_seed(
                "ULIQE.CEIP.MISC",
                "info",
                f"Annotated {len(misconceptions)} commerce/economics misconception pattern(s).",
                category="pedagogy",
            )
        )

    return {
        "domains": domains,
        "misconceptions": misconceptions,
        "accounting": accounting,
        "economics": economics,
        "finance": finance,
        "business_studies": business,
        "entrepreneurship": entrepreneurship,
        "teaching": teaching,
        "findings_seed": findings_seed,
        "provenance": "commerce_economics_intelligence.validation",
    }
