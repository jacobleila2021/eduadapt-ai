"""Tests for Universal Lesson Intelligence Validation & Quality Engine (ULIQE)."""

from __future__ import annotations

from engines.universal_lesson_intelligence import build_universal_lesson_intelligence
from engines.universal_lesson_validation import (
    ULIQE_SMOKE_OK,
    CertificationLevel,
    certify_uli,
    compare_versions,
    gate_for_downstream,
    generate_report,
    list_validation_rules,
    score_uli,
    validate_uli,
)
from engines.universal_lesson_validation.engine import UniversalLessonValidationEngine
from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
from engines.universal_lesson.profile import build_universal_lesson_profile


SAMPLE = b"""# Photosynthesis

Grade Level: 8 | Subject: Science

Students will explain how plants make food using photosynthesis.

Photosynthesis uses sunlight, water, and carbon dioxide.
Chlorophyll is the green pigment in leaves.
For example, leaves appear green because of chlorophyll.

What is the role of chlorophyll?
A common mistake is thinking plants eat soil as food.
"""


def _uli(**stem):
    envelope = ingest_source_bytes("photo.txt", SAMPLE).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return build_universal_lesson_intelligence(
        envelope,
        profile,
        stem_metadata=stem.get("stem_metadata"),
        classifications=stem.get("classifications"),
    )


def test_uliqe_smoke_constant():
    assert ULIQE_SMOKE_OK is True


def test_validate_uli_returns_report():
    report = validate_uli(_uli())
    assert report.uli_source_id
    assert report.overall_score >= 0
    assert report.certification in list(CertificationLevel)
    assert report.findings
    assert "schema" in report.rules_executed
    assert "completeness" in report.rules_executed


def test_malformed_uli_rejected():
    report = validate_uli({"educational_structure": {}})
    assert report.certification == CertificationLevel.REJECTED
    assert report.overall_score == 0


def test_score_and_certify_apis():
    uli = _uli()
    scored = score_uli(uli)
    assert "overall_score" in scored
    cert = certify_uli(uli)
    assert "certification" in cert
    assert "downstream_allowed" in cert
    assert isinstance(cert["downstream_allowed"], bool)


def test_generate_report_dict():
    data = generate_report(_uli())
    assert "findings" in data
    assert "missing_elements" in data
    assert "category_scores" in data


def test_list_validation_rules():
    rules = list_validation_rules()
    assert len(rules) >= 10
    assert {r["stage"] for r in rules} >= {"schema", "semantic", "curriculum"}


def test_gate_for_downstream():
    gate = gate_for_downstream(_uli())
    assert "allowed" in gate
    assert "report" in gate
    # Current ULI maturity: typically not Production Ready (inventory gaps).
    # Gate must not invent content to force allow.
    assert gate["allowed"] is False or gate["certification"] == "Production Ready"


def test_chemistry_failed_artifact_surfaces():
    uli = _uli(
        stem_metadata={
            "claims_found": [{"kind": "chemistry_equation", "raw": "H2 + O2 -> H2O"}],
            "artifacts": [
                {
                    "engine_id": "chemistry_balancer",
                    "ok": False,
                    "validation": "fail",
                    "validation_detail": "atom count mismatch",
                }
            ],
        }
    )
    report = validate_uli(uli)
    assert any(f.rule_id == "ULIQE.CHEM.010" for f in report.findings)
    assert report.certification == CertificationLevel.REJECTED or any(
        f.severity.value == "critical" for f in report.findings
    )


def test_compare_versions():
    uli = _uli()
    diff = compare_versions(uli, uli)
    assert diff["score_delta"] == 0.0


def test_optional_engine_process():
    uli = _uli()
    engine = UniversalLessonValidationEngine()
    bundle = engine.process({"universal_lesson_intelligence": uli})
    assert bundle.deterministic is True
    assert "uliqe" in bundle.payload


def test_does_not_mutate_uli():
    uli = _uli()
    topic = uli.educational_structure()["topic"]
    validate_uli(uli)
    assert uli.educational_structure()["topic"] == topic
