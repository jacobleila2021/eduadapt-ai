"""Biology Intelligence Pack — unit, integration, and regression tests."""

from __future__ import annotations

from engines.biology_intelligence import (
    BIOLOGY_INTELLIGENCE_SMOKE_OK,
    BiologyIntelligenceEngine,
    BiologyIntelligencePack,
    analyse_biology_lesson,
    biology_quality_signals,
    pack_health,
)
from engines.biology_intelligence.diagrams import recommend_visuals_for_text
from engines.biology_intelligence.laboratory import build_laboratory_scaffolds
from engines.biology_intelligence.misconceptions import detect_biology_misconceptions
from engines.biology_intelligence.processes import build_process_metadata
from engines.biology_intelligence.validators import collect_biology_quality_signals
from engines.biology_intelligence.worked_examples import build_worked_example_scaffolds
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


SAMPLE_BIO = b"""# Photosynthesis and Cells
Subject: Biology
Grade Level: 8
Students will explain photosynthesis and cell organelles in plant cells.
Chloroplasts contain chlorophyll. Mitochondria are involved in respiration.
Aim: Observe leaf cells under a microscope.
Apparatus: microscope, slides, coverslips, iodine stain.
Common error: students think respiration is the same as breathing.
Safety: handle slides carefully; follow lab rules.
Ecosystem note: producers form the base of food webs.
"""

SAMPLE_MISC = b"""# Cell Division
Subject: Biology
Some learners believe mitosis is the same as meiosis.
"""


def _uli_from(raw: bytes, name: str = "b.txt"):
    envelope = ingest_source_bytes(name, raw).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return build_universal_lesson_intelligence(envelope, profile, enrich=False)


def test_bip_smoke():
    reset_registry_for_tests()
    assert BIOLOGY_INTELLIGENCE_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    assert health["placeholder"] is False


def test_pack_interface_and_registration():
    reset_registry_for_tests()
    pack = get_registry().get("biology")
    assert isinstance(pack, BiologyIntelligencePack)
    assert pack.version == "1.0.0"
    assert validate_pack_interface(pack)["ok"] is True
    assert all(c.available for c in pack.capabilities())


def test_analyse_lesson_enrichment():
    uli = _uli_from(SAMPLE_BIO)
    result = analyse_biology_lesson(uli)
    assert result.ok and not result.placeholder
    assert result.subject_key == "biology"
    assert result.concept_graph.get("nodes")
    assert result.visuals
    assert result.assessment_hints
    assert result.accessibility_guidance
    assert result.tutor_guidance
    assert result.lxp_hints
    assert result.metadata.get("mutates_curriculum") is False
    domains = {d["domain"] for d in (result.metadata.get("domains") or [])}
    assert domains & {"cell_biology", "plant_biology", "physiology", "laboratory", "ecology"}


def test_misconception_detection():
    hits = detect_biology_misconceptions(
        "students think respiration is the same as breathing"
    )
    assert any(h["misconception_id"] == "bio.respiration_vs_breathing" for h in hits)
    uli = _uli_from(SAMPLE_MISC)
    result = analyse_biology_lesson(uli)
    assert any(m["misconception_id"] == "bio.mitosis_vs_meiosis" for m in result.misconceptions)


def test_diagram_and_process_metadata():
    text = SAMPLE_BIO.decode("utf-8")
    visuals = recommend_visuals_for_text(text)
    assert visuals
    assert any(v["visual_type"] in {"cell_diagram", "interactive_cell_model", "plant_structure_diagram"} for v in visuals)
    processes = build_process_metadata(text)
    assert processes.get("processes")


def test_laboratory_metadata():
    uli = _uli_from(SAMPLE_BIO)
    labs = build_laboratory_scaffolds(uli)
    assert labs
    assert labs[0].get("safety_guidance")
    assert labs[0].get("microscopy_prompt")


def test_worked_examples_exam_mode():
    uli = _uli_from(SAMPLE_BIO)
    exam_sc = build_worked_example_scaffolds(uli, exam_mode=True)
    if exam_sc:
        assert exam_sc[0].get("final_verification") is None
    protected = analyse_biology_lesson(uli, context={"exam_mode": True})
    assert any("exam" in w.lower() for w in protected.warnings)


def test_accessibility_metadata():
    uli = _uli_from(SAMPLE_BIO)
    result = analyse_biology_lesson(uli)
    ids = {r.get("recommendation") for r in result.accessibility_guidance}
    assert "simplified_biological_terminology" in ids
    assert "diagram_descriptions" in ids
    assert "accessible_laboratory_instructions" in ids


def test_sif_enrichment_uses_bip():
    reset_registry_for_tests()
    uli = _uli_from(SAMPLE_BIO)
    payload = enrich_uli_with_subject_intelligence(uli)
    assert payload["subject_key"] == "biology"
    assert payload["placeholder"] is False
    assert payload["pack_version"] == "1.0.0"
    assert payload["atie"]["tutor_guidance"]
    assert payload["aie"]["accessibility_guidance"]
    assert payload["ame"]["assessment_hints"]
    assert payload["lxp"]["visuals"]


def test_uliqe_additive_bip_signals():
    uli = _uli_from(SAMPLE_BIO)
    report = validate_uli(uli)
    rule_ids = {f.rule_id for f in report.findings}
    assert report.overall_score is not None
    assert any(rid.startswith("ULIQE.BIO") for rid in rule_ids)
    signals = collect_biology_quality_signals(uli)
    assert signals["findings_seed"]
    assert biology_quality_signals(uli)["teaching"]


def test_optional_engine():
    uli = _uli_from(SAMPLE_BIO)
    bundle = BiologyIntelligenceEngine().process({"universal_lesson_intelligence": uli})
    assert bundle.ok is True
    assert "biology_intelligence" in bundle.payload


def test_regression_no_curriculum_mutation():
    uli = _uli_from(SAMPLE_BIO)
    result = analyse_biology_lesson(uli)
    assert result.metadata.get("mutates_curriculum") is False
    sif = enrich_uli_with_subject_intelligence(uli)
    assert sif.get("mutates_curriculum") is False
    assert sif.get("mutates_engine_results") is False
