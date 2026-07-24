"""Universal Visual Intelligence Engine — unit, integration, regression tests."""

from __future__ import annotations

import pytest

from engines.universal_visual_intelligence import (
    UNIVERSAL_VISUAL_INTELLIGENCE_SMOKE_OK,
    UniversalVisualIntelligenceEngine,
    inject_into_lesson,
    pack_health,
    render_visuals_for_uli,
    uvie_quality_signals,
)
from engines.universal_visual_intelligence.intents import resolve_visual_intents
from engines.universal_visual_intelligence.priority import PRIORITY_ORDER, rank_source
from engines.visualization.priority import inject_verified_visuals_into_lesson, has_deterministic_visuals


SAMPLE = b"""# Water Cycle and Freedom Struggle
Subject: Science and Social Science
Students study the water cycle process: evaporation, condensation, precipitation.
Timeline 1857 - First War of Independence. 1947 - Independence.
Geography map of India and the Ganga river system.
Concept map of the water cycle structure.
"""


def _uli_from(raw: bytes, name: str = "uvie.txt"):
    pytest.importorskip("engines.universal_lesson_intelligence")
    pytest.importorskip("engines.universal_lesson_validation")
    from engines.knowledge_ingestion_engine.universal_ingest import ingest_source_bytes
    from engines.universal_lesson.profile import build_universal_lesson_profile
    from engines.universal_lesson_intelligence import build_universal_lesson_intelligence

    envelope = ingest_source_bytes(name, raw).to_dict()
    profile = build_universal_lesson_profile(envelope).to_dict()
    return build_universal_lesson_intelligence(envelope, profile, enrich=False)


def test_uvie_smoke():
    assert UNIVERSAL_VISUAL_INTELLIGENCE_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    assert health["visual_count"] >= 1
    assert health["policy"].startswith("prefer_official")


def test_intent_resolution():
    intents = resolve_visual_intents(
        None,
        context={
            "text": SAMPLE.decode("utf-8"),
            "sif_visuals": [
                {"visual_type": "flowchart", "label": "Process"},
                {"visual_type": "interactive_timeline", "label": "Timeline"},
                {"visual_type": "clickable_map", "label": "Map"},
            ],
        },
    )
    families = {i.family for i in intents}
    assert families & {"pedagogy", "timeline", "geography"}


def test_render_produces_deterministic_organisers():
    result = render_visuals_for_uli(
        None,
        context={
            "text": SAMPLE.decode("utf-8"),
            "topic": "Water Cycle",
            "sif_visuals": [
                {"visual_type": "flowchart", "label": "Process"},
                {"visual_type": "concept_map", "label": "Concepts"},
                {"visual_type": "interactive_timeline", "label": "Timeline"},
                {"visual_type": "clickable_map", "label": "Map"},
            ],
        },
    )
    assert result["ok"] is True
    assert result["metadata"]["mutates_curriculum"] is False
    assert result["metadata"]["generative_images_enabled"] is False
    visuals = result["visuals"]
    assert visuals
    assert all(v.get("invents_curriculum") is False for v in visuals)
    assert all((v.get("alt_text") or "").strip() for v in visuals if not v.get("placeholder"))
    sources = {v.get("source") for v in visuals}
    assert sources & {"pedagogy_organiser", "timeline_scaffold", "geography_scaffold"}


def test_pedagogy_ranks_below_stem():
    assert rank_source("ncert_figure") < rank_source("pedagogy_organiser")
    assert rank_source("matplotlib") < rank_source("pedagogy_organiser")
    assert rank_source("physics_diagram") < rank_source("timeline_scaffold")
    assert "ai_illustration" in PRIORITY_ORDER
    assert PRIORITY_ORDER.index("pedagogy_organiser") < PRIORITY_ORDER.index("ai_illustration")
    assert PRIORITY_ORDER.index("ai_illustration") < PRIORITY_ORDER.index("placeholder")


def test_inject_clears_ai_diagrams_when_deterministic():
    preferred = [
        {
            "source": "pedagogy_organiser",
            "caption": "Concept map",
            "asset_paths": [],
            "svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
            "alt_text": "Concept map",
        }
    ]
    # pedagogy_organiser is deterministic for has_deterministic_visuals?
    # has_deterministic_visuals checks source != ai_illustration — yes.
    lesson = {"mermaid_diagram": "graph TD; A-->B", "svg_diagram": "<svg/>"}
    out = inject_verified_visuals_into_lesson(lesson, preferred)
    assert has_deterministic_visuals(preferred) is True
    assert out["mermaid_diagram"] == ""
    assert out["svg_diagram"] == ""
    assert out["diagram_source"] == "deterministic_engines"

    result = render_visuals_for_uli(None, context={"text": SAMPLE.decode("utf-8"), "topic": "T"})
    injected = inject_into_lesson({"title": "t", "mermaid_diagram": "x", "svg_diagram": "y"}, result)
    assert injected.get("_meta", {}).get("uvie", {}).get("mutates_curriculum") is False


def test_uli_integration_and_uliqe():
    from engines.universal_lesson_validation import validate_uli

    uli = _uli_from(SAMPLE)
    result = render_visuals_for_uli(uli, context={"topic": "Water Cycle"})
    assert result["ok"] is True
    signals = uvie_quality_signals(uli)
    assert signals["teaching"]["visual_count"] >= 0
    report = validate_uli(uli)
    rule_ids = {f.rule_id for f in report.findings}
    assert any(rid.startswith("ULIQE.UVIE") for rid in rule_ids)


def test_optional_engine_and_lesson_pipeline():
    from engines.lesson_pipeline import process_lesson_stem

    stem = process_lesson_stem(SAMPLE.decode("utf-8"), topic="Water Cycle")
    assert "preferred_visuals" in stem
    assert "uvie" in stem
    bundle = UniversalVisualIntelligenceEngine().process(
        {"text": SAMPLE.decode("utf-8"), "topic": "Water Cycle"}
    )
    assert bundle.ok is True
    assert bundle.deterministic is True


def test_accessibility_variants_present():
    result = render_visuals_for_uli(
        None,
        context={
            "text": "Process flowchart of the water cycle structure.",
            "sif_visuals": [{"visual_type": "flowchart", "label": "Flow"}],
        },
    )
    for v in result["visuals"]:
        if v.get("placeholder"):
            continue
        assert v.get("a11y_variants")
        assert "dyslexia_friendly" in v["a11y_variants"]
