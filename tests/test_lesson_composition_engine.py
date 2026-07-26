"""Lesson Composition Engine 1.0 — composition, vocabulary, quality, smoke tests."""

from __future__ import annotations

from engines.lesson_composition_engine import (
    ADAPTIVE_VERSION_IDS,
    LESSON_COMPOSITION_ENGINE_SMOKE_OK,
    LessonCompositionEngine,
    attach_lce_to_adaptations,
    compose_lesson_package,
    pack_health,
)
from engines.lesson_composition_engine.quality_gate import evaluate_composition, gate_for_rendering
from engines.lesson_composition_engine.vocabulary import (
    compose_vocabulary_page,
    vocabulary_card_html,
)
from concept_map_builder import build_vocabulary_concept_map_svg
from structured_renderers import _word_wall_card_html


SAMPLE_TEXT = """
# The Water Cycle
Evaporation turns liquid water into water vapour when the Sun heats oceans and lakes.
Condensation forms clouds when water vapour cools into tiny droplets.
Precipitation returns water to Earth as rain, snow, or hail.
Collection gathers water in rivers, lakes, and oceans so the cycle continues.
Some students think water disappears; actually it changes into water vapour.
"""


def test_lce_smoke_ok():
    assert LESSON_COMPOSITION_ENGINE_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    assert health["smoke"] is True
    assert LessonCompositionEngine().health_check().ok is True
    print("LESSON_COMPOSITION_ENGINE_SMOKE_OK")


def test_compose_lesson_package_versions():
    profile = {
        "topic": "The Water Cycle",
        "title": "The Water Cycle",
        "concepts": [
            {"concept": "Evaporation", "explanation": "Liquid becomes vapour."},
            {"concept": "Condensation", "explanation": "Vapour cools to droplets."},
            {"concept": "Precipitation", "explanation": "Water falls from clouds."},
            {"concept": "Collection", "explanation": "Water gathers in oceans."},
        ],
        "vocabulary": [
            {"term": "Evaporation", "definition": "Water changing into water vapour."},
            {"term": "Condensation", "definition": "Water vapour cooling into droplets."},
            {"term": "Precipitation", "definition": "Water falling from clouds."},
            {"term": "Collection", "definition": "Water gathering in rivers and oceans."},
        ],
        "claim_ledger": [
            {"text": "Evaporation turns liquid water into water vapour.", "claim_id": "c1"},
            {"text": "Condensation forms clouds.", "claim_id": "c2"},
            {"text": "Precipitation returns water to Earth.", "claim_id": "c3"},
            {"text": "Collection gathers water in oceans.", "claim_id": "c4"},
        ],
    }
    package = compose_lesson_package(
        lesson_text=SAMPLE_TEXT,
        universal_profile=profile,
        context={"topic": "The Water Cycle", "subject": "science"},
    )
    assert package.vocabulary
    assert package.versions.get("standard")
    assert "adhd" in package.versions or "autism" in package.versions or len(package.versions) >= 5
    standard = package.versions["standard"]
    assert standard.get("big_idea") or standard.get("sections")
    blob = str(standard).lower()
    assert "students will explain learning objectives" not in blob
    assert package.quality is not None


def test_vocabulary_premium_cards():
    page = compose_vocabulary_page(
        [
            {"term": "Evaporation", "definition": "Water changing into water vapour."},
            {"term": "Condensation", "definition": "Water vapour cooling into droplets."},
            {"term": "Precipitation", "definition": "Water falling from clouds."},
        ],
        topic="The Water Cycle",
    )
    assert len(page.get("word_wall") or []) >= 3
    html = vocabulary_card_html(page["word_wall"][0])
    assert "Evaporation" in html or "evaporation" in html.lower()
    # Streamlit card redesign
    card = _word_wall_card_html(
        {
            "term": "evaporation",
            "definition": "Water changing into water vapour.",
            "example": "Wet clothes dry in the sun.",
            "card_number": 1,
            "emoji": "💧",
        },
        index=0,
    )
    assert "alora-vocab-number" in card
    assert "Evaporation" in card


def test_attach_lce_to_adaptations():
    adaptations = {
        "standard": {
            "big_idea": "Water moves in a cycle.",
            "sections": [
                {"title": "Evaporation", "body": "The Sun heats water and it becomes vapour."},
                {"title": "Condensation", "body": "Vapour cools and forms clouds."},
            ],
        },
        "vocabulary": {"topic": "Water", "word_wall": [{"term": "Evaporation", "definition": "Liquid to gas."}]},
        "_meta": {
            "universal_profile": {"topic": "The Water Cycle"},
            "lesson_context": {"topic": "The Water Cycle"},
        },
    }
    out = attach_lce_to_adaptations(adaptations, lesson_text=SAMPLE_TEXT, reject_on_fail=False)
    assert out["_meta"]["lce"]["enabled"] is True
    assert out.get("vocabulary")
    assert out.get("standard")


def test_quality_gate_and_relationship_map():
    lesson = {
        "big_idea": "Students understand how water moves through evaporation, condensation, precipitation and collection.",
        "sections": [
            {
                "title": "Lesson Introduction",
                "body": (
                    "Have you ever wondered where rain comes from? "
                    "The water you drink today may once have been inside a cloud. "
                    "Today we discover how water moves around our planet."
                ),
            },
            {
                "title": "Evaporation",
                "body": (
                    "When the Sun heats rivers and oceans, water changes into water vapour. "
                    "This process is called evaporation. A puddle disappears after a sunny day "
                    "because the water has evaporated into the air."
                ),
            },
            {
                "title": "Practice",
                "body": "Explain why condensation happens using evidence from the lesson.",
            },
            {
                "title": "Summary",
                "body": "Water moves in a continuous cycle through evaporation, condensation, precipitation and collection.",
            },
        ],
    }
    report = evaluate_composition(lesson, vocabulary={"word_wall": [{"term": "Evaporation"}]})
    gate = gate_for_rendering(report)
    assert "allowed" in gate

    svg = build_vocabulary_concept_map_svg(
        {
            "topic": "The Water Cycle",
            "concept_map_edges": [
                {"label": "Evaporation leads to Condensation"},
                {"label": "Condensation leads to Precipitation"},
                {"label": "Precipitation leads to Collection"},
            ],
            "word_wall": [{"term": "Evaporation"}, {"term": "Condensation"}],
        }
    )
    assert "Evaporation" in svg
    assert ADAPTIVE_VERSION_IDS
