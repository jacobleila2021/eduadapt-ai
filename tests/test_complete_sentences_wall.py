"""Learner-facing wall / study diagrams must never show half-formed sentences."""

from __future__ import annotations

from engines.lesson_composition_engine.complete_sentences import (
    ensure_complete_teaching_sentence,
    is_complete_teaching_sentence,
    strip_adaptation_suffix,
)
from engines.lesson_composition_engine.dynamic_teaching_bank import ensure_wall_from_bank
from study_diagram_builder import build_study_diagram_svg, _lesson_topic


def test_incomplete_scraps_rejected():
    assert not is_complete_teaching_sentence("which are among the most")
    assert not is_complete_teaching_sentence("Students often confuse the properties of metals and...")
    assert not is_complete_teaching_sentence("Examples: iron, copper,")
    assert ensure_complete_teaching_sentence("Examples: iron, copper,") == ""
    assert is_complete_teaching_sentence(
        "Metals are elements that are generally hard, shiny, malleable and ductile."
    )


def test_strip_adaptation_suffix():
    assert strip_adaptation_suffix("Metals and Non-metals — Parent") == "Metals and Non-metals"
    assert strip_adaptation_suffix("Lesson — Ld") == "Lesson"
    assert _lesson_topic({"title": "Lesson — Parent", "topic": "Metals and Non-metals"}) == (
        "Metals and Non-metals"
    )


def test_metals_wall_ideas_are_complete_sentences():
    wall = ensure_wall_from_bank([], [], topic="Metals and Non-metals", min_cards=3)
    assert len(wall) >= 3
    for card in wall:
        idea = str(card.get("idea") or "")
        assert is_complete_teaching_sentence(idea), idea
        assert not idea.endswith(",")
        assert "…" not in idea and "..." not in idea


def test_study_diagram_prefers_curriculum_not_ocr_scraps():
    svg = build_study_diagram_svg(
        {
            "topic": "Metals and Non-metals",
            "title": "Lesson — Parent",
            "sections": [
                {
                    "title": "Physical Properties of Metals",
                    "role": "concept",
                    "body": "gold, silver, which are among the most",
                },
                {
                    "title": "Common Mistakes to Avoid",
                    "role": "common_misconception",
                    "body": "Students often confuse the properties of metals and...",
                },
                {
                    "title": "Home Explanation",
                    "role": "parent_support",
                    "body": "Your child is learning Lesson with the family tonight.",
                },
            ],
        }
    )
    low = svg.lower()
    assert "lesson — parent" not in low
    assert "lesson — ld" not in low
    assert "among the most" not in low
    assert "must know" not in low
    assert "metal" in low or "malleab" in low or "ductil" in low
