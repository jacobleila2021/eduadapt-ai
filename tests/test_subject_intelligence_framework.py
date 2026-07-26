"""Subject Intelligence Framework — core architecture tests."""

from __future__ import annotations

from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
from engines.subject_intelligence_framework import (
    SUBJECT_INTELLIGENCE_FRAMEWORK_SMOKE_OK,
    PlaceholderSubjectPack,
    detect_subject_from_uli,
    enrich_uli_with_subject_intelligence,
    get_registry,
    list_subject_packs,
    lxp_hook_catalogue,
    reset_registry_for_tests,
    validate_pack_interface,
    validate_registry,
)
from engines.subject_intelligence_framework.engine import SubjectIntelligenceFrameworkEngine
from engines.subject_intelligence_framework.schemas import SubjectId
from engines.universal_lesson.profile import build_universal_lesson_profile
from engines.universal_lesson_intelligence import build_universal_lesson_intelligence
from engines.universal_lesson_intelligence.pipeline import build_uli_context


SAMPLE_BIO = b"""# Photosynthesis
Grade Level: 8 | Subject: Science
Students will explain how plants make food using photosynthesis.
Chlorophyll is the green pigment in leaves.
"""

SAMPLE_MATH = b"""# Linear Equations
Subject: Mathematics
Solve for x: 2x + 5 = 15
"""


def test_sif_smoke():
    assert SUBJECT_INTELLIGENCE_FRAMEWORK_SMOKE_OK is True


def test_registry_has_placeholder_subjects():
    reset_registry_for_tests()
    keys = set(get_registry().keys())
    for required in (
        "mathematics",
        "physics",
        "chemistry",
        "biology",
        "english",
        "social_science",
        "computer_science",
        "history",
        "geography",
        "general",
    ):
        assert required in keys
    packs = list_subject_packs()
    # All subject intelligence packs through WLIP are production; `general` remains placeholder.
    production = {
        "mathematics",
        "physics",
        "chemistry",
        "biology",
        "english",
        "social_science",
        "history",
        "geography",
        "civics",
        "environmental_science",
        "computer_science",
        "commerce",
        "economics",
        "business_studies",
        "languages",
    }
    for key in production:
        pack = next(p for p in packs if p["key"] == key)
        assert pack.get("placeholder") is False, key
    assert all(p.get("placeholder") for p in packs if p["key"] not in production)


def test_interface_compliance_all_packs():
    report = validate_registry()
    assert report["ok"] is True
    assert report["pack_count"] >= 15


def test_placeholder_analyse_is_empty_structured():
    reset_registry_for_tests()
    pack = get_registry().get("general")
    assert isinstance(pack, PlaceholderSubjectPack)
    envelope = ingest_source_bytes("m.txt", SAMPLE_MATH).to_dict()
    uli = build_universal_lesson_intelligence(envelope, enrich=False)
    result = pack.analyse_lesson(uli)
    assert result.placeholder is True
    assert result.ok is True
    assert result.concept_graph == {}
    assert result.misconceptions == []


def test_detect_subject_from_uli_math():
    envelope = ingest_source_bytes("m.txt", SAMPLE_MATH).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    uli = build_universal_lesson_intelligence(envelope, profile, enrich=False)
    detection = detect_subject_from_uli(uli)
    assert detection.subject_key in {"mathematics", "general"}
    # Declared Subject: Mathematics should win
    assert detection.subject_key == "mathematics"
    assert detection.confidence >= 0.7


def test_enrich_uli_payload_shape():
    envelope = ingest_source_bytes("b.txt", SAMPLE_BIO).to_dict()
    uli = build_universal_lesson_intelligence(envelope, enrich=False)
    payload = enrich_uli_with_subject_intelligence(uli)
    assert payload["framework"] == "subject_intelligence_framework"
    assert payload["mutates_curriculum"] is False
    assert "atie" in payload and "lxp" in payload
    assert "lxp_hook_catalogue" in payload
    assert len(lxp_hook_catalogue()) >= 4


def test_uli_pipeline_includes_sif():
    envelope = ingest_source_bytes("b.txt", SAMPLE_BIO).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    ctx = build_uli_context(
        source_envelope=envelope,
        universal_profile=profile,
        stem_metadata={"artifacts": [], "claims_found": []},
        enrich=True,
    )
    assert "subject_intelligence" in ctx
    assert ctx["subject_intelligence"].get("subject_key")


def test_optional_engine():
    envelope = ingest_source_bytes("b.txt", SAMPLE_BIO).to_dict()
    uli = build_universal_lesson_intelligence(envelope, enrich=False)
    bundle = SubjectIntelligenceFrameworkEngine().process(
        {"universal_lesson_intelligence": uli}
    )
    assert bundle.ok is True
    assert "sif" in bundle.payload


def test_custom_pack_registration():
    reset_registry_for_tests()

    class TinyPack(PlaceholderSubjectPack):
        def __init__(self):
            super().__init__(SubjectId("mathematics", "Mathematics", "stem"))
            self.version = "1.0.0-test"

    get_registry().register(TinyPack(), overwrite=True)
    pack = get_registry().get("mathematics")
    assert pack.version == "1.0.0-test"
    assert validate_pack_interface(pack)["ok"] is True
    # Restore production packs for subsequent test modules in the same session.
    reset_registry_for_tests()
