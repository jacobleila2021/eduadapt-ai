"""Metals and Non-metals — source Qs, vocab hygiene, answer match, hide answers."""

from __future__ import annotations

from engines.lesson_composition_engine.canonical import build_canonical_lesson
from engines.lesson_composition_engine.composer import compose_vocabulary_from_clg
from engines.lesson_composition_engine.vocab_quality import (
    canonical_definition,
    is_ocr_garbage_claim,
    student_safe_definition,
)
from structured_renderers import _parse_qa_pairs


SOURCE = """
Metals and Non-metals

Metals are generally hard, shiny, malleable, ductile and good conductors.
Non-metals are generally dull, brittle and poor conductors.

QUESTIONS
1. Explain the terms malleable and ductile.
2. What is the product formed when magnesium burns in air?
3. List two properties of non-metals.
4. Which metal is liquid at room temperature?

For performing Activities 3.1 to 3.6, collect the samples of following metals –
iron, copper, aluminium, magnesium, sodium, lead, zinc and any other metal that is easily available.
CAUTION: Always handle sodium metal with care.
You will be learning more about these metal oxides in the next section.
"""


def test_lab_instructions_are_garbage():
    assert is_ocr_garbage_claim(
        "For performing Activities 3.1 to 3.6, collect the samples of following metals – iron, copper"
    )
    assert not student_safe_definition(
        "You will be learning more about these metal oxides in the next section."
    )


def test_vocab_uses_bank_not_activity_text():
    page = compose_vocabulary_from_clg(
        {
            "topic": "Metals and Non-metals",
            "facts": [
                {
                    "text": (
                        "For performing Activities 3.1 to 3.6, collect the samples of following "
                        "metals – iron, copper, aluminium, magnesium, sodium, lead, zinc"
                    )
                }
            ],
            "claim_texts": [
                "Metals are generally hard, shiny, malleable and ductile.",
                "Non-metals are generally dull and brittle.",
            ],
            "core_concepts": [{"name": "Metal"}, {"name": "Non-metal"}, {"name": "Iron"}],
            "vocabulary": [],
        }
    )
    wall = page.get("word_wall") or []
    blob = " ".join(str(w.get("definition") or "") for w in wall).lower()
    assert "for performing" not in blob
    assert "collect the samples" not in blob
    assert any("malleable" in str(w.get("definition") or "").lower() for w in wall) or any(
        str(w.get("term") or "").lower() == "metal" for w in wall
    )


def test_master_prefers_source_questions_not_classmate():
    page = build_canonical_lesson(
        {
            "topic": "Metals and Non-metals",
            "source_text": SOURCE,
            "verified_claims": [
                "Metals are generally hard, shiny, malleable, ductile and good conductors.",
                "Non-metals are generally dull, brittle and poor conductors.",
            ],
            "concepts": [{"name": "Metal"}, {"name": "Non-metal"}, {"name": "Malleability"}],
            "assessment_outcomes": [
                {"prompt": "Explain the terms malleable and ductile.", "marks": 2},
                {"prompt": "List two properties of non-metals.", "marks": 2},
                {"prompt": "What is the product formed when magnesium burns in air?", "marks": 2},
            ],
        }
    )
    bodies = "\n".join(str(s.get("body") or "") for s in page.get("sections") or [])
    assert "classmate confuses" not in bodies.lower()
    assert "malleable" in bodies.lower() or "non-metal" in bodies.lower()
    # Lab chrome must not teach
    assert "for performing activit" not in bodies.lower()


def test_nonmetal_answer_matches_stem():
    from engines.lesson_composition_engine.canonical import build_canonical_lesson

    page = build_canonical_lesson(
        {
            "topic": "Metals and Non-metals",
            "source_text": SOURCE,
            "verified_claims": [
                "Metals are generally hard, shiny, malleable, ductile and good conductors.",
                "Non-metals are generally dull, brittle and poor conductors of heat and electricity.",
            ],
            "concepts": [{"name": "Metal"}, {"name": "Non-metal"}],
            "assessment_outcomes": [
                {"prompt": "Explain non-metals using evidence from the lesson.", "marks": 2},
            ],
        }
    )
    practice = next(
        s for s in page["sections"] if s.get("role") == "practice_question"
    )
    body = str(practice.get("body") or "").lower()
    if "non-metal" in body or "non metals" in body:
        # Answer near the non-metal question should not be only the metals definition.
        assert "dull" in body or "brittle" in body or "poor conductors" in body


def test_parse_hides_broken_answer_markers():
    pairs = _parse_qa_pairs(
        "3. List two properties of non-metals. - { Answer Non-metals are generally poor conductors.)"
    )
    assert pairs
    assert "list two properties" in pairs[0]["question"].lower()
    assert "poor conductors" in pairs[0]["answer"].lower()
    assert "{" not in pairs[0]["answer"]


def test_canonical_metal_defs():
    assert "malleable" in canonical_definition("Metal").lower()
    assert "brittle" in canonical_definition("Non-metals").lower() or "poor" in canonical_definition(
        "Non-metals"
    ).lower()
    assert "magnesium oxide" in canonical_definition("Metal oxide").lower() or "oxide" in canonical_definition(
        "Metal oxide"
    ).lower()
