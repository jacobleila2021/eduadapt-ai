"""Computer Science Intelligence Pack — unit, integration, regression tests."""

from __future__ import annotations

from engines.computer_science_intelligence import (
    COMPUTER_SCIENCE_INTELLIGENCE_SMOKE_OK,
    ComputerScienceIntelligenceEngine,
    ComputerScienceIntelligencePack,
    analyse_computer_science_lesson,
    computer_science_quality_signals,
    pack_health,
)
from engines.computer_science_intelligence.algorithms import algorithms_metadata
from engines.computer_science_intelligence.artificial_intelligence import artificial_intelligence_metadata
from engines.computer_science_intelligence.databases import databases_metadata
from engines.computer_science_intelligence.misconceptions import detect_computer_science_misconceptions
from engines.computer_science_intelligence.networking import networking_metadata
from engines.computer_science_intelligence.programming import programming_metadata
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


SAMPLE_CS = b"""# Introduction to Algorithms and Programming
Subject: Computer Science
Grade Level: 10
Students will use computational thinking: decomposition, abstraction, and algorithm design.
They will write programs with variables, loops, and functions, then debug with a trace table.
Algorithms: sorting and searching with Big-O complexity annotations.
Databases: relational schema, SQL queries, and normalisation.
Networking: TCP/IP protocols, DNS, and routing; cybersecurity: encryption and authentication.
Artificial intelligence concepts and ethical AI / data bias (conceptual only).
Common error: learners believe equals means mathematical equality in code.
"""

SAMPLE_MISC = b"""# Machine Learning Basics
Subject: Computer Science
Some learners believe AI thinks like a human and that more training data always improves models.
"""


def _uli_from(raw: bytes, name: str = "cs.txt"):
    envelope = ingest_source_bytes(name, raw).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return build_universal_lesson_intelligence(envelope, profile, enrich=False)


def test_csip_smoke():
    reset_registry_for_tests()
    assert COMPUTER_SCIENCE_INTELLIGENCE_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    assert health["placeholder"] is False
    assert health["smoke"] is True


def test_registration():
    reset_registry_for_tests()
    pack = get_registry().get("computer_science")
    assert isinstance(pack, ComputerScienceIntelligencePack)
    assert pack.version == "1.0.0"
    assert validate_pack_interface(pack)["ok"] is True


def test_analyse_lesson_enrichment():
    uli = _uli_from(SAMPLE_CS)
    result = analyse_computer_science_lesson(uli)
    assert result.ok and not result.placeholder
    assert result.subject_key == "computer_science"
    assert result.visuals
    assert result.assessment_hints
    assert result.accessibility_guidance
    assert result.tutor_guidance
    assert result.lxp_hints
    assert result.metadata.get("mutates_curriculum") is False
    assert result.metadata.get("programming", {}).get("reveals_assessment_answers") is False
    assert result.metadata.get("artificial_intelligence", {}).get("replaces_ai_computation_engines") is False
    domains = {d["domain"] for d in (result.metadata.get("domains") or [])}
    assert domains & {"programming", "algorithms", "databases", "networking"}


def test_programming_algorithms_databases_networking_ai():
    text = SAMPLE_CS.decode("utf-8")
    domains = [
        {"domain": "programming", "score": 2},
        {"domain": "algorithms", "score": 2},
        {"domain": "databases", "score": 1},
        {"domain": "networking", "score": 1},
        {"domain": "artificial_intelligence", "score": 1},
    ]
    assert programming_metadata(text, domains)["foci"]
    assert algorithms_metadata(text, domains)["complexity_annotations"] is True
    assert databases_metadata(text, domains)["invents_query_results"] is False
    assert networking_metadata(text, domains)["foci"]
    assert artificial_intelligence_metadata(text, domains)["conceptual_only"] is True


def test_misconception_detection():
    hits = detect_computer_science_misconceptions(
        "learners believe equals means mathematical equality in code"
    )
    assert any(h["misconception_id"] == "cs.equals_assigns" for h in hits)
    uli = _uli_from(SAMPLE_MISC)
    result = analyse_computer_science_lesson(uli)
    ids = {m["misconception_id"] for m in result.misconceptions}
    assert "cs.ai_thinks_like_humans" in ids or "cs.ml_more_data_always" in ids


def test_sif_enrichment_uses_csip():
    reset_registry_for_tests()
    uli = _uli_from(SAMPLE_CS)
    payload = enrich_uli_with_subject_intelligence(uli)
    assert payload["subject_key"] == "computer_science"
    assert payload["placeholder"] is False
    assert payload["atie"]["tutor_guidance"]
    assert payload["aie"]["accessibility_guidance"]
    assert payload["ame"]["assessment_hints"]
    assert payload["lxp"]["visuals"]


def test_uliqe_additive_csip_signals():
    uli = _uli_from(SAMPLE_CS)
    report = validate_uli(uli)
    rule_ids = {f.rule_id for f in report.findings}
    assert report.overall_score is not None
    assert any(rid.startswith("ULIQE.CS") for rid in rule_ids)
    assert any(rid.startswith("ULIQE.CS.CSIP") for rid in rule_ids)
    assert computer_science_quality_signals(uli)["teaching"]


def test_optional_engine_and_regression():
    uli = _uli_from(SAMPLE_CS)
    bundle = ComputerScienceIntelligenceEngine().process({"universal_lesson_intelligence": uli})
    assert bundle.ok is True
    result = analyse_computer_science_lesson(uli)
    assert result.metadata.get("mutates_curriculum") is False
    sif = enrich_uli_with_subject_intelligence(uli)
    assert sif.get("mutates_curriculum") is False
    assert sif.get("mutates_engine_results") is False


def test_exam_mode_does_not_reveal_answers():
    uli = _uli_from(SAMPLE_CS)
    result = analyse_computer_science_lesson(uli, context={"exam_mode": True})
    assert result.metadata.get("exam_mode") is True
    assert result.metadata.get("programming", {}).get("reveals_assessment_answers") is False
    assert any("exam" in w.lower() or "protected" in w.lower() for w in result.warnings)
