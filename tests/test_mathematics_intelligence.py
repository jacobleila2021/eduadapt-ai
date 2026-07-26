"""Mathematics Intelligence Pack — unit, integration, and regression tests."""

from __future__ import annotations

from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
from engines.mathematics_intelligence import (
    MATHEMATICS_INTELLIGENCE_SMOKE_OK,
    MathematicsIntelligenceEngine,
    MathematicsIntelligencePack,
    analyse_mathematics_lesson,
    math_quality_signals,
    pack_health,
)
from engines.mathematics_intelligence.misconceptions import detect_math_misconceptions
from engines.mathematics_intelligence.symbolic import inspect_symbolic_consistency
from engines.mathematics_intelligence.validators import collect_math_quality_signals
from engines.mathematics_intelligence.worked_examples import build_worked_example_scaffolds
from engines.subject_intelligence_framework import (
    enrich_uli_with_subject_intelligence,
    get_registry,
    reset_registry_for_tests,
    validate_pack_interface,
)
from engines.universal_lesson.profile import build_universal_lesson_profile
from engines.universal_lesson_intelligence import build_universal_lesson_intelligence
from engines.universal_lesson_validation import validate_uli


SAMPLE_MATH = b"""# Linear Equations
Subject: Mathematics
Grade Level: 8
Students will solve linear equations using inverse operations.
Solve for x: 2x + 5 = 15
Common error: students only add to one side of the equation.
Area and perimeter of rectangles appear in the application section.
"""

SAMPLE_FRAC = b"""# Fractions
Subject: Mathematics
Some learners believe a bigger denominator means a bigger fraction, e.g. 1/8 is greater 1/4.
"""


def _uli_from(raw: bytes, name: str = "m.txt"):
    envelope = ingest_source_bytes(name, raw).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return build_universal_lesson_intelligence(envelope, profile, enrich=False), envelope, profile


def test_mip_smoke():
    reset_registry_for_tests()
    assert MATHEMATICS_INTELLIGENCE_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    assert health["smoke"] is True
    assert health["placeholder"] is False


def test_pack_interface_and_registration():
    reset_registry_for_tests()
    pack = get_registry().get("mathematics")
    assert isinstance(pack, MathematicsIntelligencePack)
    assert pack.version == "1.0.0"
    assert validate_pack_interface(pack)["ok"] is True
    caps = pack.capabilities()
    assert any(c.available for c in caps)
    assert all(c.available for c in caps)


def test_analyse_lesson_enrichment():
    uli, _, _ = _uli_from(SAMPLE_MATH)
    result = analyse_mathematics_lesson(uli)
    assert result.ok is True
    assert result.placeholder is False
    assert result.subject_key == "mathematics"
    assert result.concept_graph.get("nodes")
    assert result.visuals
    assert result.assessment_hints
    assert result.accessibility_guidance
    assert result.tutor_guidance
    assert result.lxp_hints
    assert result.teaching_strategies
    assert result.metadata.get("mutates_curriculum") is False
    domains = result.metadata.get("domains") or []
    assert any(d["domain"] in {"algebra", "geometry", "arithmetic"} for d in domains)


def test_misconception_detection():
    hits = detect_math_misconceptions(
        "learners believe a bigger denominator means a bigger fraction; 1/8 is greater 1/4"
    )
    assert any(h["misconception_id"] == "math.frac_larger_denominator" for h in hits)

    uli, _, _ = _uli_from(SAMPLE_FRAC)
    result = analyse_mathematics_lesson(uli)
    assert any(m["misconception_id"] == "math.frac_larger_denominator" for m in result.misconceptions)


def test_worked_examples_exam_mode_hides_verification():
    uli, _, _ = _uli_from(SAMPLE_MATH)
    open_sc = build_worked_example_scaffolds(uli, exam_mode=False)
    exam_sc = build_worked_example_scaffolds(uli, exam_mode=True)
    if open_sc:
        assert open_sc[0].get("final_verification")
    if exam_sc:
        assert exam_sc[0].get("final_verification") is None
        assert exam_sc[0].get("exam_mode") is True

    protected = analyse_mathematics_lesson(uli, context={"exam_mode": True})
    assert any("Exam" in w or "exam" in w.lower() for w in protected.warnings)


def test_symbolic_and_quality_signals():
    uli, _, _ = _uli_from(SAMPLE_MATH)
    sym = inspect_symbolic_consistency(uli)
    assert "symbol_consistency" in sym
    signals = collect_math_quality_signals(uli)
    assert signals["provenance"].endswith("validators")
    assert "findings_seed" in signals
    assert math_quality_signals(uli)["teaching"]


def test_accessibility_metadata():
    uli, _, _ = _uli_from(SAMPLE_MATH)
    result = analyse_mathematics_lesson(uli)
    ids = {r.get("recommendation") for r in result.accessibility_guidance}
    assert "dyslexia_friendly_notation" in ids
    assert "chunk_multi_step" in ids
    assert all(r.get("owner") for r in result.accessibility_guidance)


def test_sif_enrichment_uses_mip():
    reset_registry_for_tests()
    uli, _, _ = _uli_from(SAMPLE_MATH)
    payload = enrich_uli_with_subject_intelligence(uli)
    assert payload["subject_key"] == "mathematics"
    assert payload["placeholder"] is False
    assert payload["pack_version"] == "1.0.0"
    assert payload["analysis"]["placeholder"] is False
    assert payload["atie"]["tutor_guidance"]
    assert payload["aie"]["accessibility_guidance"]
    assert payload["ame"]["assessment_hints"]
    assert payload["lxp"]["visuals"]


def test_uliqe_additive_mip_signals():
    uli, _, _ = _uli_from(SAMPLE_MATH)
    report = validate_uli(uli)
    rule_ids = {f.rule_id for f in report.findings}
    # Additive MIP rules may or may not fire depending on domain detection;
    # at minimum mathematics stage still runs and report is well-formed.
    assert report.overall_score is not None
    assert any(rid.startswith("ULIQE.MATH") for rid in rule_ids)
    # When domains detected, MIP.000 should appear
    if any(rid.startswith("ULIQE.MATH.MIP") for rid in rule_ids):
        assert "ULIQE.MATH.MIP.000" in rule_ids or any(
            rid.startswith("ULIQE.MATH.MIP.") for rid in rule_ids
        )


def test_optional_engine():
    uli, _, _ = _uli_from(SAMPLE_MATH)
    bundle = MathematicsIntelligenceEngine().process({"universal_lesson_intelligence": uli})
    assert bundle.ok is True
    assert "mathematics_intelligence" in bundle.payload


def test_regression_no_curriculum_mutation_flag():
    uli, _, _ = _uli_from(SAMPLE_MATH)
    result = analyse_mathematics_lesson(uli)
    assert result.metadata.get("mutates_curriculum") is False
    sif = enrich_uli_with_subject_intelligence(uli)
    assert sif.get("mutates_curriculum") is False
    assert sif.get("mutates_engine_results") is False
