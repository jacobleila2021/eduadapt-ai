"""World Languages Intelligence Pack — unit, integration, regression tests."""

from __future__ import annotations

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
from engines.world_languages_intelligence import (
    WORLD_LANGUAGES_INTELLIGENCE_SMOKE_OK,
    WorldLanguagesIntelligenceEngine,
    WorldLanguagesIntelligencePack,
    analyse_world_languages_lesson,
    list_language_plugins,
    pack_health,
    register_language_plugin,
    world_languages_quality_signals,
)
from engines.world_languages_intelligence.grammar import grammar_metadata
from engines.world_languages_intelligence.misconceptions import detect_world_languages_misconceptions
from engines.world_languages_intelligence.pronunciation import pronunciation_metadata
from engines.world_languages_intelligence.reading import reading_metadata
from engines.world_languages_intelligence.vocabulary import vocabulary_metadata
from engines.world_languages_intelligence.writing import writing_metadata
from engines.world_languages_intelligence.accessibility import world_languages_accessibility_for_uli


SAMPLE_WL = b"""# French Pronunciation and Grammar
Subject: Languages
Grade Level: 9
Students will practise French pronunciation with IPA, stress, syllables, and minimal pairs.
Grammar: verb conjugation, agreement, and word order; vocabulary with cognates and word families.
Reading fluency and comprehension with context clues; writing sentence formation and cohesion.
Speaking conversation practice and listening comprehension.
Translation: contextual meaning and register; culture and idiomatic usage.
Common error: learners pronounce every language like English spelling.
"""

SAMPLE_MISC = b"""# Translation Myths
Subject: Languages
Spanish and Hindi lesson notes.
Some learners believe translation is always word-for-word and that each word has only one meaning.
"""


def _uli_from(raw: bytes, name: str = "wl.txt"):
    envelope = ingest_source_bytes(name, raw).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return build_universal_lesson_intelligence(envelope, profile, enrich=False)


def test_wlip_smoke():
    reset_registry_for_tests()
    assert WORLD_LANGUAGES_INTELLIGENCE_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    assert health["placeholder"] is False
    assert health["language_plugins"] >= 16


def test_registration_and_plugins():
    reset_registry_for_tests()
    pack = get_registry().get("languages")
    assert isinstance(pack, WorldLanguagesIntelligencePack)
    assert pack.version == "1.0.0"
    assert validate_pack_interface(pack)["ok"] is True
    ids = {p["id"] for p in list_language_plugins()}
    assert {"french", "spanish", "hindi", "malayalam", "japanese", "arabic", "english"} <= ids
    assert any(p.get("integration_only") for p in list_language_plugins() if p["id"] == "english")


def test_analyse_lesson_enrichment():
    uli = _uli_from(SAMPLE_WL)
    result = analyse_world_languages_lesson(uli)
    assert result.ok and not result.placeholder
    assert result.subject_key == "languages"
    assert result.visuals
    assert result.assessment_hints
    assert result.accessibility_guidance
    assert result.tutor_guidance
    assert result.lxp_hints
    assert result.metadata.get("mutates_curriculum") is False
    assert result.metadata.get("pronunciation", {}).get("invents_audio") is False
    assert result.metadata.get("translation", {}).get("replaces_translation_engines") is False
    assert result.metadata.get("english_subject_owner") == "english_language_intelligence"
    langs = {lang["id"] for lang in (result.metadata.get("languages") or [])}
    assert "french" in langs
    domains = {d["domain"] for d in (result.metadata.get("domains") or [])}
    assert domains & {"pronunciation", "grammar", "vocabulary", "reading"}


def test_pronunciation_grammar_vocabulary_reading_writing():
    text = SAMPLE_WL.decode("utf-8")
    domains = [
        {"domain": "pronunciation", "score": 2},
        {"domain": "grammar", "score": 2},
        {"domain": "vocabulary", "score": 1},
        {"domain": "reading", "score": 1},
        {"domain": "writing", "score": 1},
    ]
    langs = [{"id": "french", "pronunciation_notes": ["liaison"], "grammar_highlights": ["gender"]}]
    assert pronunciation_metadata(text, domains, langs)["foci"]
    assert grammar_metadata(text, domains, langs)["invents_rules"] is False
    assert vocabulary_metadata(text, domains)["invents_definitions"] is False
    assert reading_metadata(text, domains)["read_aloud"] is True
    assert writing_metadata(text, domains)["reveals_assessment_answers"] is False


def test_misconception_and_accessibility():
    hits = detect_world_languages_misconceptions(
        "learners pronounce every language like English spelling"
    )
    assert any(h["misconception_id"] == "wl.pronounce_like_english" for h in hits)
    uli = _uli_from(SAMPLE_MISC)
    result = analyse_world_languages_lesson(uli)
    ids = {m["misconception_id"] for m in result.misconceptions}
    assert "wl.word_for_word" in ids or "wl.vocab_one_meaning" in ids
    a11y = world_languages_accessibility_for_uli(uli)
    assert a11y
    assert any("dyslexia" in str(a).lower() or a.get("recommendation") == "dyslexia_friendly_reading" for a in a11y)


def test_plugin_extension_without_engine_change():
    plugin = register_language_plugin(
        "swahili",
        {
            "code": "sw",
            "name": "Swahili",
            "scripts": ["Latin"],
            "direction": "ltr",
            "pronunciation_notes": ["syllable_timed"],
            "grammar_highlights": ["noun_classes"],
        },
        overwrite=True,
    )
    assert plugin["id"] == "swahili"
    assert any(p["id"] == "swahili" for p in list_language_plugins())


def test_sif_enrichment_uses_wlip():
    reset_registry_for_tests()
    uli = _uli_from(SAMPLE_WL)
    payload = enrich_uli_with_subject_intelligence(uli)
    assert payload["subject_key"] == "languages"
    assert payload["placeholder"] is False
    assert payload["atie"]["tutor_guidance"]
    assert payload["aie"]["accessibility_guidance"]
    assert payload["ame"]["assessment_hints"]
    assert payload["lxp"]["visuals"]


def test_uliqe_additive_wlip_signals():
    uli = _uli_from(SAMPLE_WL)
    report = validate_uli(uli)
    rule_ids = {f.rule_id for f in report.findings}
    assert report.overall_score is not None
    assert any(rid.startswith("ULIQE.WLIP") for rid in rule_ids)
    assert any(
        rid in rule_ids
        for rid in (
            "ULIQE.WLIP.PRONUNCIATION",
            "ULIQE.WLIP.GRAMMAR",
            "ULIQE.WLIP.READING",
            "ULIQE.WLIP.WRITING",
            "ULIQE.WLIP.VOCABULARY",
        )
    )
    assert world_languages_quality_signals(uli)["teaching"]


def test_optional_engine_and_regression():
    uli = _uli_from(SAMPLE_WL)
    bundle = WorldLanguagesIntelligenceEngine().process({"universal_lesson_intelligence": uli})
    assert bundle.ok is True
    result = analyse_world_languages_lesson(uli)
    assert result.metadata.get("mutates_curriculum") is False
    sif = enrich_uli_with_subject_intelligence(uli)
    assert sif.get("mutates_curriculum") is False
    assert sif.get("mutates_engine_results") is False
    # ELIP still owns english
    assert get_registry().get("english").subject.key == "english"
    assert not getattr(get_registry().get("english"), "version", "").endswith("placeholder")
