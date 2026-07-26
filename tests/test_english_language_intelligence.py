"""English Language Intelligence Pack — unit, integration, regression tests."""

from __future__ import annotations

from engines.english_language_intelligence import (
    ENGLISH_LANGUAGE_INTELLIGENCE_SMOKE_OK,
    EnglishLanguageIntelligenceEngine,
    EnglishLanguageIntelligencePack,
    analyse_english_lesson,
    english_quality_signals,
    pack_health,
)
from engines.english_language_intelligence.grammar import grammar_metadata
from engines.english_language_intelligence.literature import literature_metadata
from engines.english_language_intelligence.misconceptions import detect_english_misconceptions
from engines.english_language_intelligence.reading import reading_metadata
from engines.english_language_intelligence.vocabulary import vocabulary_metadata
from engines.english_language_intelligence.writing import writing_metadata
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


SAMPLE_ENG = b"""# Reading Comprehension and Vocabulary
Subject: English
Grade Level: 8
Students will identify the main idea and supporting details in a passage.
They will use context clues for academic vocabulary and practise narrative writing.
Literature focus: theme and figurative language in a short poem.
Common error: learners believe theme is the same as topic.
Listening and speaking: oral summary of the poem with clear pronunciation.
"""

SAMPLE_MISC = b"""# Grammar Voice
Subject: English
Some students believe passive voice is always wrong.
"""


def _uli_from(raw: bytes, name: str = "e.txt"):
    envelope = ingest_source_bytes(name, raw).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return build_universal_lesson_intelligence(envelope, profile, enrich=False)


def test_elip_smoke():
    reset_registry_for_tests()
    assert ENGLISH_LANGUAGE_INTELLIGENCE_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    assert health["placeholder"] is False


def test_pack_interface_and_registration():
    reset_registry_for_tests()
    pack = get_registry().get("english")
    assert isinstance(pack, EnglishLanguageIntelligencePack)
    assert pack.version == "1.0.0"
    assert validate_pack_interface(pack)["ok"] is True
    assert all(c.available for c in pack.capabilities())


def test_analyse_lesson_enrichment():
    uli = _uli_from(SAMPLE_ENG)
    result = analyse_english_lesson(uli)
    assert result.ok and not result.placeholder
    assert result.subject_key == "english"
    assert result.visuals
    assert result.assessment_hints
    assert result.accessibility_guidance
    assert result.tutor_guidance
    assert result.lxp_hints
    assert result.metadata.get("mutates_curriculum") is False
    assert result.metadata.get("reading")
    assert result.metadata.get("vocabulary")
    assert result.metadata.get("writing", {}).get("generates_assessment_answers") is False
    domains = {d["domain"] for d in (result.metadata.get("domains") or [])}
    assert domains & {"reading", "vocabulary", "writing", "literature"}


def test_reading_vocabulary_grammar_literature():
    text = SAMPLE_ENG.decode("utf-8")
    domains = [{"domain": "reading", "score": 1}, {"domain": "vocabulary", "score": 1}]
    assert reading_metadata(text, domains)["capabilities"]
    assert vocabulary_metadata(text)["entries"]
    assert grammar_metadata("subject-verb agreement and tenses", [{"domain": "grammar", "score": 1}])["foci"]
    lit = literature_metadata(text, [{"domain": "literature", "score": 1}])
    assert lit["lenses"]
    assert writing_metadata(text, [{"domain": "writing", "score": 1}])["modes"]


def test_misconception_detection():
    hits = detect_english_misconceptions("learners believe theme is the same as topic")
    assert any(h["misconception_id"] == "eng.theme_equals_topic" for h in hits)
    uli = _uli_from(SAMPLE_MISC)
    result = analyse_english_lesson(uli)
    assert any(m["misconception_id"] == "eng.passive_always_wrong" for m in result.misconceptions)


def test_sif_enrichment_uses_elip():
    reset_registry_for_tests()
    uli = _uli_from(SAMPLE_ENG)
    payload = enrich_uli_with_subject_intelligence(uli)
    assert payload["subject_key"] == "english"
    assert payload["placeholder"] is False
    assert payload["pack_version"] == "1.0.0"
    assert payload["atie"]["tutor_guidance"]
    assert payload["aie"]["accessibility_guidance"]
    assert payload["ame"]["assessment_hints"]
    assert payload["lxp"]["visuals"]


def test_uliqe_additive_elip_signals():
    uli = _uli_from(SAMPLE_ENG)
    report = validate_uli(uli)
    rule_ids = {f.rule_id for f in report.findings}
    assert report.overall_score is not None
    assert any(rid.startswith("ULIQE.ENG") for rid in rule_ids)
    assert any(rid.startswith("ULIQE.ENG.ELIP") for rid in rule_ids)
    assert english_quality_signals(uli)["teaching"]


def test_optional_engine_and_exam_mode():
    uli = _uli_from(SAMPLE_ENG)
    bundle = EnglishLanguageIntelligenceEngine().process({"universal_lesson_intelligence": uli})
    assert bundle.ok is True
    protected = analyse_english_lesson(uli, context={"exam_mode": True})
    assert any("exam" in w.lower() for w in protected.warnings)


def test_regression_no_curriculum_mutation():
    uli = _uli_from(SAMPLE_ENG)
    result = analyse_english_lesson(uli)
    assert result.metadata.get("mutates_curriculum") is False
    sif = enrich_uli_with_subject_intelligence(uli)
    assert sif.get("mutates_curriculum") is False
    assert sif.get("mutates_engine_results") is False
