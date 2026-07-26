"""Chemistry Intelligence Pack — unit, integration, and regression tests."""

from __future__ import annotations

from engines.chemistry_intelligence import (
    CHEMISTRY_INTELLIGENCE_SMOKE_OK,
    ChemistryIntelligenceEngine,
    ChemistryIntelligencePack,
    analyse_chemistry_lesson,
    chemistry_quality_signals,
    pack_health,
)
from engines.chemistry_intelligence.equations import inspect_equations_and_notation
from engines.chemistry_intelligence.laboratory import build_laboratory_scaffolds
from engines.chemistry_intelligence.misconceptions import detect_chemistry_misconceptions
from engines.chemistry_intelligence.molecular_models import build_molecular_metadata
from engines.chemistry_intelligence.validators import collect_chemistry_quality_signals
from engines.chemistry_intelligence.worked_examples import build_worked_example_scaffolds
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


SAMPLE_CHEM = b"""# Acids, Bases and Stoichiometry
Subject: Chemistry
Grade Level: 10
Students will balance chemical equations and calculate moles.
Reaction: HCl(aq) + NaOH(aq) -> NaCl(aq) + H2O(l)
Aim: Investigate neutralisation by titration.
Apparatus: burette, pipette, conical flask, indicator.
Common error: students think a strong acid is the same as a concentrated acid.
Safety: wear goggles; handle acids carefully.
"""

SAMPLE_MISC = b"""# Atoms and Molecules
Subject: Chemistry
Some learners believe an atom is the same as a molecule and that O2 is an atom.
"""


def _uli_from(raw: bytes, name: str = "c.txt"):
    envelope = ingest_source_bytes(name, raw).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return build_universal_lesson_intelligence(envelope, profile, enrich=False)


def test_cip_smoke():
    reset_registry_for_tests()
    assert CHEMISTRY_INTELLIGENCE_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    assert health["placeholder"] is False


def test_pack_interface_and_registration():
    reset_registry_for_tests()
    pack = get_registry().get("chemistry")
    assert isinstance(pack, ChemistryIntelligencePack)
    assert pack.version == "1.0.0"
    assert validate_pack_interface(pack)["ok"] is True
    assert all(c.available for c in pack.capabilities())


def test_analyse_lesson_enrichment():
    uli = _uli_from(SAMPLE_CHEM)
    result = analyse_chemistry_lesson(uli)
    assert result.ok and not result.placeholder
    assert result.subject_key == "chemistry"
    assert result.concept_graph.get("nodes")
    assert result.visuals
    assert result.assessment_hints
    assert result.accessibility_guidance
    assert result.tutor_guidance
    assert result.lxp_hints
    assert result.metadata.get("mutates_curriculum") is False
    domains = {d["domain"] for d in (result.metadata.get("domains") or [])}
    assert domains & {"acids_bases", "stoichiometry", "reactions", "laboratory"}


def test_misconception_detection():
    hits = detect_chemistry_misconceptions(
        "students think a strong acid is the same as a concentrated acid"
    )
    assert any(h["misconception_id"] == "chem.strong_vs_concentrated" for h in hits)
    uli = _uli_from(SAMPLE_MISC)
    result = analyse_chemistry_lesson(uli)
    assert any(m["misconception_id"] == "chem.atom_vs_molecule" for m in result.misconceptions)


def test_laboratory_metadata():
    uli = _uli_from(SAMPLE_CHEM)
    labs = build_laboratory_scaffolds(uli)
    assert labs
    assert labs[0].get("safety_precautions")
    assert labs[0].get("hazard_warnings")
    assert labs[0].get("variables")


def test_equation_and_formula_signals():
    uli = _uli_from(SAMPLE_CHEM)
    # Attach equation-like stem via analyse path (source text still drives domains)
    eq = inspect_equations_and_notation(uli)
    assert "balancing_signal" in eq
    assert "notation_consistency" in eq
    mol = build_molecular_metadata(SAMPLE_CHEM.decode("utf-8"))
    assert "formula_candidates" in mol
    assert mol.get("representation_hooks")
    signals = collect_chemistry_quality_signals(uli)
    assert signals["findings_seed"]
    assert chemistry_quality_signals(uli)["teaching"]


def test_worked_examples_exam_mode():
    uli = _uli_from(SAMPLE_CHEM)
    exam_sc = build_worked_example_scaffolds(uli, exam_mode=True)
    if exam_sc:
        assert exam_sc[0].get("final_verification") is None
    protected = analyse_chemistry_lesson(uli, context={"exam_mode": True})
    assert any("exam" in w.lower() for w in protected.warnings)


def test_accessibility_metadata():
    uli = _uli_from(SAMPLE_CHEM)
    result = analyse_chemistry_lesson(uli)
    ids = {r.get("recommendation") for r in result.accessibility_guidance}
    assert "simplified_chemistry_language" in ids
    assert "molecule_descriptions" in ids


def test_sif_enrichment_uses_cip():
    reset_registry_for_tests()
    uli = _uli_from(SAMPLE_CHEM)
    payload = enrich_uli_with_subject_intelligence(uli)
    assert payload["subject_key"] == "chemistry"
    assert payload["placeholder"] is False
    assert payload["pack_version"] == "1.0.0"
    assert payload["atie"]["tutor_guidance"]
    assert payload["aie"]["accessibility_guidance"]
    assert payload["ame"]["assessment_hints"]
    assert payload["lxp"]["visuals"]


def test_uliqe_additive_cip_signals():
    uli = _uli_from(SAMPLE_CHEM)
    report = validate_uli(uli)
    rule_ids = {f.rule_id for f in report.findings}
    assert report.overall_score is not None
    assert any(rid.startswith("ULIQE.CHEM") for rid in rule_ids)


def test_optional_engine():
    uli = _uli_from(SAMPLE_CHEM)
    bundle = ChemistryIntelligenceEngine().process({"universal_lesson_intelligence": uli})
    assert bundle.ok is True
    assert "chemistry_intelligence" in bundle.payload


def test_regression_no_curriculum_mutation():
    uli = _uli_from(SAMPLE_CHEM)
    result = analyse_chemistry_lesson(uli)
    assert result.metadata.get("mutates_curriculum") is False
    sif = enrich_uli_with_subject_intelligence(uli)
    assert sif.get("mutates_curriculum") is False
    assert sif.get("mutates_engine_results") is False
