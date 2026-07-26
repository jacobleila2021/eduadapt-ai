"""Milestone 2.1 — Universal Lesson Intelligence facade (behaviour-preserving)."""

from __future__ import annotations

import copy

from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
from engines.universal_lesson.profile import build_universal_lesson_profile
from engines.universal_lesson_intelligence import (
    ULI_SCHEMA_VERSION,
    build_universal_lesson_intelligence,
)
from engines.universal_lesson_intelligence.facade import UniversalLessonIntelligence


SAMPLE = b"""# Photosynthesis

Grade Level: 8 | Subject: Science

Students will explain how plants make food.

Photosynthesis uses sunlight, water, and carbon dioxide.
Chlorophyll is the green pigment in leaves.

What is the role of chlorophyll?
"""


def _envelope_and_profile():
    envelope = ingest_source_bytes("photosynthesis.txt", SAMPLE).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return envelope, profile


def test_facade_wraps_existing_profile_without_mutation():
    envelope, profile = _envelope_and_profile()
    profile_snapshot = copy.deepcopy(profile)
    envelope_snapshot = copy.deepcopy(envelope)

    uli = build_universal_lesson_intelligence(envelope, profile)

    assert uli.schema_version == ULI_SCHEMA_VERSION
    assert uli.source_id == profile["source_id"]
    assert dict(uli.universal_profile) == profile_snapshot
    assert dict(uli.source_envelope) == envelope_snapshot
    # Caller-owned objects unchanged
    assert profile == profile_snapshot
    assert envelope == envelope_snapshot


def test_facade_rejects_mutation_of_views():
    envelope, profile = _envelope_and_profile()
    original_topic = profile["topic"]
    uli = build_universal_lesson_intelligence(envelope, profile)
    try:
        uli.universal_profile["topic"] = "MUTATED"  # type: ignore[index]
        mutated = True
    except TypeError:
        mutated = False
    assert mutated is False
    assert profile["topic"] == original_topic


def test_semantic_layers_expose_existing_fields():
    envelope, profile = _envelope_and_profile()
    uli = build_universal_lesson_intelligence(envelope, profile)

    edu = uli.educational_structure()
    assert edu["title"] == profile["title"]
    assert edu["topic"] == profile["topic"]
    assert edu["language"] == profile["language"]
    assert dict(edu["curriculum_resolution"]) == profile["curriculum_resolution"]
    assert edu["duration_estimate"] is None

    learn = uli.learning_structure()
    assert list(learn["learning_objectives"]) == profile["learning_objectives"]
    assert list(learn["key_concepts"]) == profile["concepts"]
    assert list(learn["vocabulary"]) == profile["vocabulary"]
    assert list(learn["skills"]) == profile["skills"]
    assert list(learn["definitions"]) == []
    assert list(learn["prior_knowledge"]) == []

    assess = uli.assessment_structure()
    assert list(assess["assessment_opportunities"]) == profile["assessment_opportunities"]

    a11y = uli.accessibility_structure()
    assert dict(a11y["reading_level"]) == profile["difficulty"]
    assert dict(a11y["age_estimate"]) == profile["age_estimate"]
    assert list(a11y["executive_function_demands"]) == []


def test_stem_structure_passthrough_only_when_supplied():
    envelope, profile = _envelope_and_profile()
    empty = build_universal_lesson_intelligence(envelope, profile)
    assert list(empty.stem_structure()["claims_found"]) == []
    assert list(empty.stem_structure()["artifacts"]) == []

    stem = {
        "claims_found": [{"kind": "chemistry_equation", "raw": "H2 + O2 -> H2O"}],
        "artifacts": [{"engine_id": "chemistry_balancer"}],
        "routing_warnings": [],
        "preferred_visuals": [],
    }
    uli = build_universal_lesson_intelligence(
        envelope, profile, stem_metadata=stem
    )
    assert list(uli.stem_structure()["chemical_equations"]) == stem["claims_found"]
    assert list(uli.stem_structure()["artifacts"]) == stem["artifacts"]


def test_build_without_profile_uses_existing_builder():
    envelope, _ = _envelope_and_profile()
    expected = build_universal_lesson_profile(envelope).to_dict()
    uli = build_universal_lesson_intelligence(envelope)
    assert dict(uli.universal_profile)["topic"] == expected["topic"]
    assert dict(uli.universal_profile)["claim_ledger"] == expected["claim_ledger"]


def test_from_artifacts_matches_constructor():
    envelope, profile = _envelope_and_profile()
    a = UniversalLessonIntelligence.from_artifacts(envelope, profile)
    b = build_universal_lesson_intelligence(envelope, profile)
    assert dict(a.educational_structure()) == dict(b.educational_structure())


def test_claim_ledger_matches_profile():
    envelope, profile = _envelope_and_profile()
    uli = build_universal_lesson_intelligence(envelope, profile)
    assert list(uli.claim_ledger) == profile["claim_ledger"]


def test_learning_resources_tables_and_examples():
    envelope, profile = _envelope_and_profile()
    uli = build_universal_lesson_intelligence(envelope, profile)
    resources = uli.learning_resources()
    assert list(resources["worked_examples"]) == profile["examples"]
    # Unenriched: diagrams come from profile visual opportunities
    assert list(resources["diagrams"]) == profile["visual_opportunities"]
    assert isinstance(list(resources["tables"]), list)
    assert isinstance(list(resources["images"]), list)
