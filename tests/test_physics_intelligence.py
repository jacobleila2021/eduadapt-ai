"""Physics Intelligence Pack — unit, integration, and regression tests."""

from __future__ import annotations

from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
from engines.physics_intelligence import (
    PHYSICS_INTELLIGENCE_SMOKE_OK,
    PhysicsIntelligenceEngine,
    PhysicsIntelligencePack,
    analyse_physics_lesson,
    pack_health,
    physics_quality_signals,
)
from engines.physics_intelligence.experiments import build_experiment_scaffolds
from engines.physics_intelligence.misconceptions import detect_physics_misconceptions
from engines.physics_intelligence.units_formulas import inspect_formula_and_units
from engines.physics_intelligence.validators import collect_physics_quality_signals
from engines.physics_intelligence.worked_examples import build_worked_example_scaffolds
from engines.subject_intelligence_framework import (
    enrich_uli_with_subject_intelligence,
    get_registry,
    reset_registry_for_tests,
    validate_pack_interface,
)
from engines.universal_lesson.profile import build_universal_lesson_profile
from engines.universal_lesson_intelligence import build_universal_lesson_intelligence
from engines.universal_lesson_validation import validate_uli


SAMPLE_PHYS = b"""# Forces and Motion
Subject: Physics
Grade Level: 9
Students will apply Newton's laws using free-body force diagrams.
A net force of 10 N acts on a 2 kg mass. Acceleration a = F/m.
Common error: students think a force is needed to keep an object moving.
Aim: Investigate how force affects acceleration.
Equipment: trolley, pulley, slotted masses, ticker timer.
Independent variable: force. Dependent variable: acceleration.
"""

SAMPLE_MISC = b"""# Weight and Mass
Subject: Physics
Some learners believe weight is the same as mass and write kg of weight.
"""


def _uli_from(raw: bytes, name: str = "p.txt"):
    envelope = ingest_source_bytes(name, raw).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return build_universal_lesson_intelligence(envelope, profile, enrich=False)


def test_pip_smoke():
    reset_registry_for_tests()
    assert PHYSICS_INTELLIGENCE_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    assert health["placeholder"] is False


def test_pack_interface_and_registration():
    reset_registry_for_tests()
    pack = get_registry().get("physics")
    assert isinstance(pack, PhysicsIntelligencePack)
    assert pack.version == "1.0.0"
    assert validate_pack_interface(pack)["ok"] is True
    assert all(c.available for c in pack.capabilities())


def test_analyse_lesson_enrichment():
    uli = _uli_from(SAMPLE_PHYS)
    result = analyse_physics_lesson(uli)
    assert result.ok and not result.placeholder
    assert result.subject_key == "physics"
    assert result.concept_graph.get("nodes")
    assert result.visuals
    assert result.assessment_hints
    assert result.accessibility_guidance
    assert result.tutor_guidance
    assert result.lxp_hints
    assert result.teaching_strategies
    assert result.metadata.get("mutates_curriculum") is False
    domains = {d["domain"] for d in (result.metadata.get("domains") or [])}
    assert domains & {"forces", "motion", "mechanics"}


def test_misconception_detection():
    hits = detect_physics_misconceptions(
        "students think a force is needed to keep an object moving"
    )
    assert any(h["misconception_id"] == "phys.force_needed_for_motion" for h in hits)
    uli = _uli_from(SAMPLE_MISC)
    result = analyse_physics_lesson(uli)
    assert any(m["misconception_id"] == "phys.weight_vs_mass" for m in result.misconceptions)


def test_experiment_scaffolds():
    uli = _uli_from(SAMPLE_PHYS)
    exps = build_experiment_scaffolds(uli)
    assert exps
    assert exps[0].get("variables")
    assert exps[0].get("safety_notes")
    assert "cer" in (exps[0].get("frameworks") or [])


def test_worked_examples_exam_mode():
    uli = _uli_from(SAMPLE_PHYS)
    open_sc = build_worked_example_scaffolds(uli, exam_mode=False)
    exam_sc = build_worked_example_scaffolds(uli, exam_mode=True)
    if exam_sc:
        assert exam_sc[0].get("final_verification") is None
    protected = analyse_physics_lesson(uli, context={"exam_mode": True})
    assert any("exam" in w.lower() for w in protected.warnings)


def test_units_formulas_and_quality():
    uli = _uli_from(SAMPLE_PHYS)
    units = inspect_formula_and_units(uli)
    assert "unit_consistency" in units
    assert "formula_consistency" in units
    signals = collect_physics_quality_signals(uli)
    assert signals["findings_seed"]
    assert physics_quality_signals(uli)["teaching"]


def test_accessibility_metadata():
    uli = _uli_from(SAMPLE_PHYS)
    result = analyse_physics_lesson(uli)
    ids = {r.get("recommendation") for r in result.accessibility_guidance}
    assert "simplified_physics_language" in ids
    assert "diagram_descriptions" in ids


def test_sif_enrichment_uses_pip():
    reset_registry_for_tests()
    uli = _uli_from(SAMPLE_PHYS)
    payload = enrich_uli_with_subject_intelligence(uli)
    assert payload["subject_key"] == "physics"
    assert payload["placeholder"] is False
    assert payload["pack_version"] == "1.0.0"
    assert payload["atie"]["tutor_guidance"]
    assert payload["aie"]["accessibility_guidance"]
    assert payload["ame"]["assessment_hints"]
    assert payload["lxp"]["visuals"]


def test_uliqe_additive_pip_signals():
    uli = _uli_from(SAMPLE_PHYS)
    report = validate_uli(uli)
    rule_ids = {f.rule_id for f in report.findings}
    assert report.overall_score is not None
    assert any(rid.startswith("ULIQE.PHYS") for rid in rule_ids)


def test_optional_engine():
    uli = _uli_from(SAMPLE_PHYS)
    bundle = PhysicsIntelligenceEngine().process({"universal_lesson_intelligence": uli})
    assert bundle.ok is True
    assert "physics_intelligence" in bundle.payload


def test_regression_no_curriculum_mutation():
    uli = _uli_from(SAMPLE_PHYS)
    result = analyse_physics_lesson(uli)
    assert result.metadata.get("mutates_curriculum") is False
    sif = enrich_uli_with_subject_intelligence(uli)
    assert sif.get("mutates_curriculum") is False
    assert sif.get("mutates_engine_results") is False
