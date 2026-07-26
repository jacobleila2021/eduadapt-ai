"""Social Science Intelligence Pack — unit, integration, regression tests."""

from __future__ import annotations

from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
from engines.social_science_intelligence import (
    SOCIAL_SCIENCE_INTELLIGENCE_SMOKE_OK,
    SocialScienceIntelligenceEngine,
    SocialScienceIntelligencePack,
    analyse_social_science_lesson,
    pack_health,
    social_science_quality_signals,
)
from engines.social_science_intelligence.civics import civics_metadata
from engines.social_science_intelligence.economics import economics_metadata
from engines.social_science_intelligence.geography import geography_metadata
from engines.social_science_intelligence.history import history_metadata
from engines.social_science_intelligence.maps import map_metadata
from engines.social_science_intelligence.misconceptions import detect_social_science_misconceptions
from engines.social_science_intelligence.timelines import timeline_metadata
from engines.subject_intelligence_framework import (
    enrich_uli_with_subject_intelligence,
    get_registry,
    reset_registry_for_tests,
    validate_pack_interface,
)
from engines.universal_lesson.profile import build_universal_lesson_profile
from engines.universal_lesson_intelligence import build_universal_lesson_intelligence
from engines.universal_lesson_validation import validate_uli


SAMPLE_SOC = b"""# The Freedom Struggle and Indian Geography
Subject: Social Science
Grade Level: 8
Students will place key events on a timeline from 1857 to 1947 and explain cause and effect.
They will use a map of British India and discuss democracy and the Constitution.
Economics link: trade and markets under colonial rule.
Primary source: excerpt from a speech (evaluate purpose and limitations).
Common error: learners believe primary sources are always reliable.
"""

SAMPLE_MISC = b"""# Climate Basics
Subject: Geography
Some learners believe climate is the same as weather.
"""


def _uli_from(raw: bytes, name: str = "s.txt"):
    envelope = ingest_source_bytes(name, raw).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return build_universal_lesson_intelligence(envelope, profile, enrich=False)


def test_ssip_smoke():
    reset_registry_for_tests()
    assert SOCIAL_SCIENCE_INTELLIGENCE_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    assert health["family_registered"] is True
    assert health["placeholder"] is False


def test_family_registration():
    reset_registry_for_tests()
    for key in ("social_science", "history", "geography", "civics", "environmental_science"):
        pack = get_registry().get(key)
        assert isinstance(pack, SocialScienceIntelligencePack)
        assert pack.version == "1.0.0"
        assert validate_pack_interface(pack)["ok"] is True


def test_analyse_lesson_enrichment():
    uli = _uli_from(SAMPLE_SOC)
    result = analyse_social_science_lesson(uli)
    assert result.ok and not result.placeholder
    assert result.subject_key == "social_science"
    assert result.visuals
    assert result.assessment_hints
    assert result.accessibility_guidance
    assert result.tutor_guidance
    assert result.lxp_hints
    assert result.metadata.get("mutates_curriculum") is False
    assert result.metadata.get("history")
    assert result.metadata.get("timelines", {}).get("invents_events") is False
    assert result.metadata.get("maps", {}).get("invents_geodata") is False
    domains = {d["domain"] for d in (result.metadata.get("domains") or [])}
    assert domains & {"history", "geography", "civics", "economics"}


def test_history_geography_civics_economics():
    text = SAMPLE_SOC.decode("utf-8")
    domains = [
        {"domain": "history", "score": 2},
        {"domain": "geography", "score": 2},
        {"domain": "civics", "score": 1},
        {"domain": "economics", "score": 1},
    ]
    assert history_metadata(text, domains)["foci"]
    assert geography_metadata(text, domains)["foci"]
    assert civics_metadata(text, domains)["foci"]
    assert economics_metadata(text, domains)["foci"]


def test_timeline_and_map_metadata():
    text = SAMPLE_SOC.decode("utf-8")
    domains = [{"domain": "history", "score": 1}, {"domain": "geography", "score": 1}]
    tl = timeline_metadata(text, domains)
    assert tl["applicable"] is True
    assert tl["invents_events"] is False
    mp = map_metadata(text, domains)
    assert mp["applicable"] is True
    assert mp["invents_geodata"] is False


def test_misconception_detection():
    hits = detect_social_science_misconceptions(
        "learners believe primary sources are always reliable"
    )
    assert any(h["misconception_id"] == "soc.primary_source_always_true" for h in hits)
    uli = _uli_from(SAMPLE_MISC)
    result = analyse_social_science_lesson(uli)
    assert any(m["misconception_id"] == "soc.climate_equals_weather" for m in result.misconceptions)


def test_sif_enrichment_uses_ssip():
    reset_registry_for_tests()
    uli = _uli_from(SAMPLE_SOC)
    payload = enrich_uli_with_subject_intelligence(uli)
    assert payload["subject_key"] in {
        "social_science",
        "history",
        "geography",
        "civics",
        "environmental_science",
    }
    assert payload["placeholder"] is False
    assert payload["atie"]["tutor_guidance"]
    assert payload["aie"]["accessibility_guidance"]
    assert payload["ame"]["assessment_hints"]
    assert payload["lxp"]["visuals"]


def test_uliqe_additive_ssip_signals():
    uli = _uli_from(SAMPLE_SOC)
    report = validate_uli(uli)
    rule_ids = {f.rule_id for f in report.findings}
    assert report.overall_score is not None
    assert any(rid.startswith("ULIQE.SOC") for rid in rule_ids)
    assert any(rid.startswith("ULIQE.SOC.SSIP") for rid in rule_ids)
    assert social_science_quality_signals(uli)["teaching"]


def test_optional_engine_and_regression():
    uli = _uli_from(SAMPLE_SOC)
    bundle = SocialScienceIntelligenceEngine().process({"universal_lesson_intelligence": uli})
    assert bundle.ok is True
    result = analyse_social_science_lesson(uli)
    assert result.metadata.get("mutates_curriculum") is False
    sif = enrich_uli_with_subject_intelligence(uli)
    assert sif.get("mutates_curriculum") is False
    assert sif.get("mutates_engine_results") is False
