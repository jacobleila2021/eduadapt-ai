"""Fractions uploads must compose without crashing on empty point banks."""

from __future__ import annotations

from engines.lesson_composition_engine.canonical import build_canonical_lesson
from engines.lesson_composition_engine.vocab_quality import canonical_definition


def test_fraction_bank_definitions():
    assert "numerator" in canonical_definition("Fraction").lower()
    assert "top" in canonical_definition("Numerator").lower()
    assert "bottom" in canonical_definition("Denominator").lower()


def test_fractions_canonical_lesson_builds():
    board = {
        "topic": "Fractions",
        "subject": "mathematics",
        "verified_claims": [
            "A fraction represents a part of a whole.",
            "The numerator is the top number and the denominator is the bottom number.",
            "1/2 and 2/4 are equivalent fractions.",
        ],
        "concepts": [
            {"name": "Fraction", "explanation": ""},
            {"name": "Numerator", "explanation": ""},
            {"name": "Denominator", "explanation": ""},
        ],
        "misconceptions": [],
        "learning_goals": [],
        "examples": [],
        "assessment_objectives": [],
    }
    lesson = build_canonical_lesson(board)
    assert lesson.get("sections")
    roles = {str(s.get("role") or "") for s in lesson["sections"]}
    assert "hots_question" in roles or "practice_question" in roles
    blob = " ".join(str(s.get("body") or "") for s in lesson["sections"]).lower()
    assert "numerator" in blob or "fraction" in blob
