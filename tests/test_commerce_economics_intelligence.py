"""Commerce & Economics Intelligence Pack — unit, integration, regression tests."""

from __future__ import annotations

from engines.commerce_economics_intelligence import (
    COMMERCE_ECONOMICS_INTELLIGENCE_SMOKE_OK,
    CommerceEconomicsIntelligenceEngine,
    CommerceEconomicsIntelligencePack,
    analyse_commerce_economics_lesson,
    commerce_economics_quality_signals,
    pack_health,
)
from engines.commerce_economics_intelligence.accounting import accounting_metadata
from engines.commerce_economics_intelligence.business_studies import business_studies_metadata
from engines.commerce_economics_intelligence.economics import economics_metadata
from engines.commerce_economics_intelligence.entrepreneurship import entrepreneurship_metadata
from engines.commerce_economics_intelligence.finance import finance_metadata
from engines.commerce_economics_intelligence.misconceptions import detect_commerce_economics_misconceptions
from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
from engines.subject_intelligence_framework import (
    enrich_uli_with_subject_intelligence,
    get_registry,
    reset_registry_for_tests,
    validate_pack_interface,
)
from engines.universal_lesson.profile import build_universal_lesson_profile
from engines.universal_lesson_intelligence import build_universal_lesson_intelligence
from engines.universal_lesson_validation import validate_uli


SAMPLE_CE = b"""# Accounting, Markets, and Enterprise
Subject: Commerce
Grade Level: 11
Students will post journal entries to the ledger and prepare a trial balance and financial statements.
Economics: demand, supply, elasticity, and inflation with fiscal and monetary policy cause-effect.
Business studies: management principles, leadership, and decision making.
Finance: banking, investment, budgeting, and risk management.
Entrepreneurship: business planning, market validation, and the business model canvas.
Marketing: branding, pricing, and market research.
Common error: learners believe debit always means increase and that profit equals cash.
"""

SAMPLE_MISC = b"""# Start-up Myths
Subject: Business Studies
Some learners believe a good idea alone is a successful business and that marketing is only advertising.
"""


def _uli_from(raw: bytes, name: str = "ce.txt"):
    envelope = ingest_source_bytes(name, raw).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return build_universal_lesson_intelligence(envelope, profile, enrich=False)


def test_ceip_smoke():
    reset_registry_for_tests()
    assert COMMERCE_ECONOMICS_INTELLIGENCE_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    assert health["family_registered"] is True
    assert health["placeholder"] is False


def test_family_registration():
    reset_registry_for_tests()
    for key in ("commerce", "economics", "business_studies"):
        pack = get_registry().get(key)
        assert isinstance(pack, CommerceEconomicsIntelligencePack)
        assert pack.version == "1.0.0"
        assert validate_pack_interface(pack)["ok"] is True


def test_analyse_lesson_enrichment():
    uli = _uli_from(SAMPLE_CE)
    result = analyse_commerce_economics_lesson(uli)
    assert result.ok and not result.placeholder
    assert result.subject_key == "commerce"
    assert result.visuals
    assert result.assessment_hints
    assert result.accessibility_guidance
    assert result.tutor_guidance
    assert result.lxp_hints
    assert result.metadata.get("mutates_curriculum") is False
    assert result.metadata.get("accounting", {}).get("reveals_assessment_answers") is False
    assert result.metadata.get("economics", {}).get("concept_relationships") is True
    domains = {d["domain"] for d in (result.metadata.get("domains") or [])}
    assert domains & {"accounting", "economics", "finance", "entrepreneurship"}


def test_accounting_economics_business_finance_entrepreneurship():
    text = SAMPLE_CE.decode("utf-8")
    domains = [
        {"domain": "accounting", "score": 2},
        {"domain": "economics", "score": 2},
        {"domain": "business_studies", "score": 1},
        {"domain": "finance", "score": 1},
        {"domain": "entrepreneurship", "score": 1},
    ]
    assert accounting_metadata(text, domains)["foci"]
    assert economics_metadata(text, domains)["cause_effect_mappings"]
    assert business_studies_metadata(text, domains)["foci"]
    assert finance_metadata(text, domains)["invents_returns"] is False
    assert entrepreneurship_metadata(text, domains)["business_model_canvas"] is True


def test_misconception_detection():
    hits = detect_commerce_economics_misconceptions(
        "learners believe debit always means increase and that profit equals cash"
    )
    ids = {h["misconception_id"] for h in hits}
    assert "ce.debit_always_increase" in ids
    assert "ce.profit_equals_cash" in ids
    uli = _uli_from(SAMPLE_MISC)
    result = analyse_commerce_economics_lesson(uli)
    misc_ids = {m["misconception_id"] for m in result.misconceptions}
    assert "ce.idea_is_business" in misc_ids or "ce.marketing_only_ads" in misc_ids


def test_sif_enrichment_uses_ceip():
    reset_registry_for_tests()
    uli = _uli_from(SAMPLE_CE)
    payload = enrich_uli_with_subject_intelligence(uli)
    assert payload["subject_key"] in {"commerce", "economics", "business_studies"}
    assert payload["placeholder"] is False
    assert payload["atie"]["tutor_guidance"]
    assert payload["aie"]["accessibility_guidance"]
    assert payload["ame"]["assessment_hints"]
    assert payload["lxp"]["visuals"]


def test_uliqe_additive_ceip_signals():
    uli = _uli_from(SAMPLE_CE)
    report = validate_uli(uli)
    rule_ids = {f.rule_id for f in report.findings}
    assert report.overall_score is not None
    assert any(rid.startswith("ULIQE.CEIP") for rid in rule_ids)
    assert any(rid in rule_ids for rid in (
        "ULIQE.CEIP.ACCOUNTING",
        "ULIQE.CEIP.ECONOMICS",
        "ULIQE.CEIP.FINANCE",
        "ULIQE.CEIP.BUSINESS",
        "ULIQE.CEIP.ENTREPRENEURSHIP",
    ))
    assert commerce_economics_quality_signals(uli)["teaching"]


def test_optional_engine_and_regression():
    uli = _uli_from(SAMPLE_CE)
    bundle = CommerceEconomicsIntelligenceEngine().process({"universal_lesson_intelligence": uli})
    assert bundle.ok is True
    result = analyse_commerce_economics_lesson(uli)
    assert result.metadata.get("mutates_curriculum") is False
    sif = enrich_uli_with_subject_intelligence(uli)
    assert sif.get("mutates_curriculum") is False
    assert sif.get("mutates_engine_results") is False


def test_exam_mode_does_not_reveal_answers():
    uli = _uli_from(SAMPLE_CE)
    result = analyse_commerce_economics_lesson(uli, context={"exam_mode": True})
    assert result.metadata.get("exam_mode") is True
    assert result.metadata.get("accounting", {}).get("reveals_assessment_answers") is False
    assert any("exam" in w.lower() or "protected" in w.lower() for w in result.warnings)
