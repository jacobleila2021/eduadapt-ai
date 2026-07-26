"""Milestone 2.2 — ULI semantic enrichment & STEM integration tests."""

from __future__ import annotations

from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
from engines.universal_lesson.profile import build_universal_lesson_profile
from engines.universal_lesson_intelligence import (
    ULI_MILESTONE_2_2_SMOKE_OK,
    ULI_SCHEMA_VERSION,
    build_enriched_universal_lesson_intelligence,
    build_universal_lesson_intelligence,
)
from engines.universal_lesson_validation import validate_uli


SAMPLE = b"""# Photosynthesis

Grade Level: 8 | Subject: Science

Students will explain how plants make food using photosynthesis.

Photosynthesis uses sunlight, water, and carbon dioxide.
Chlorophyll is the green pigment in leaves.
The equation is often written: 6CO2 + 6H2O -> C6H12O6 + 6O2

What is the role of chlorophyll?
"""


def _base():
    envelope = ingest_source_bytes("photo.txt", SAMPLE).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return envelope, profile


def test_milestone_2_2_smoke():
    assert ULI_MILESTONE_2_2_SMOKE_OK is True
    assert ULI_SCHEMA_VERSION.startswith("3.2")


def test_unenriched_facade_still_works():
    envelope, profile = _base()
    uli = build_universal_lesson_intelligence(envelope, profile, enrich=False)
    assert uli.enriched is False
    assert list(uli.stem_structure().get("claims_found") or []) == []
    assert uli.educational_structure()["title"] == profile["title"]


def test_enriched_attaches_stem_and_declared_meta():
    envelope, profile = _base()
    uli = build_enriched_universal_lesson_intelligence(envelope, profile)
    assert uli.enriched is True
    edu = uli.educational_structure()
    assert edu.get("subject")
    assert "Science" in str(edu.get("subject"))
    stem = uli.stem_structure()
    # Chemistry equation in sample should yield at least a claim or empty with warnings
    assert "claims_found" in stem
    assert "formula_inventory" in stem
    assert "content_classifications" in stem


def test_new_accessors_exist_and_immutable():
    envelope, profile = _base()
    uli = build_enriched_universal_lesson_intelligence(envelope, profile)
    for name in (
        "diagram_structure",
        "voice_structure",
        "analytics_structure",
        "knowledge_graph_structure",
        "tutor_structure",
        "companion_structure",
        "lxp_structure",
    ):
        payload = getattr(uli, name)()
        assert payload is not None
        try:
            payload["mut"] = 1  # type: ignore[index]
            mutated = True
        except TypeError:
            mutated = False
        assert mutated is False


def test_semantic_bundle_cached():
    envelope, profile = _base()
    uli = build_enriched_universal_lesson_intelligence(envelope, profile)
    a = uli.semantic_bundle()
    b = uli.semantic_bundle()
    assert a is b
    assert a["enriched"] is True
    assert "knowledge_graph_structure" in a
    assert "enrichment_sources" in a


def test_ensure_enriched_idempotent():
    envelope, profile = _base()
    uli = build_universal_lesson_intelligence(envelope, profile)
    enriched = uli.ensure_enriched()
    assert enriched.enriched is True
    again = enriched.ensure_enriched()
    assert again is enriched


def test_enriched_profile_view_does_not_mutate_profile():
    envelope, profile = _base()
    snapshot = dict(profile)
    uli = build_enriched_universal_lesson_intelligence(envelope, profile)
    view = uli.enriched_profile_view()
    assert view.get("subject") or view.get("uli_schema_version")
    assert profile == snapshot


def test_uliqe_accepts_enriched_uli_without_scoring_code_change():
    envelope, profile = _base()
    uli = build_enriched_universal_lesson_intelligence(envelope, profile)
    report = validate_uli(uli)
    assert report.findings
    assert report.uli_source_id == uli.source_id
    # Richer STEM may surface chem findings; scoring module untouched.
    assert report.overall_score >= 0


def test_knowledge_graph_references_lesson_node():
    envelope, profile = _base()
    uli = build_enriched_universal_lesson_intelligence(envelope, profile)
    kg = uli.knowledge_graph_structure()
    types = {n.get("type") for n in kg.get("nodes") or []}
    assert "lesson" in types
