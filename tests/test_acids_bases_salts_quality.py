"""Acids, Bases and Salts — OCR junk must never become learner content."""

from __future__ import annotations

from engines.lesson_composition_engine.canonical import build_canonical_lesson
from engines.lesson_composition_engine.intelligence_board import build_lesson_intelligence_board
from engines.lesson_composition_engine.vocab_quality import (
    canonical_definition,
    clean_learner_claim,
    is_junk_term,
    is_ocr_garbage_claim,
    normalize_vocab_items,
    question_what_is,
    repair_ocr_prose,
)

OCR_INTRO = (
    "Acids, Bases and Salts 2CHAPTER Y ou have lear nt in your pr evious classes "
    "that the sour and bitter tastes of food are due to acids and bases, respectively, present in them."
)

GARBLED = (
    "UNDERST UNDERSTUNDERST ANDING THE CHEMICANDING THE CHEMIC AL PROPERTIES OF "
    "ACIDS AND BASESACIDS AND BASES"
)


def test_repair_ocr_prose_fixes_ncert_spacing():
    fixed = repair_ocr_prose(OCR_INTRO)
    assert "CHAPTER" not in fixed.upper() or "2CHAPTER" not in fixed
    assert "lear nt" not in fixed
    assert "pr evious" not in fixed
    assert "Y ou" not in fixed


def test_ocr_chapter_intro_is_garbage():
    assert is_ocr_garbage_claim(OCR_INTRO)
    assert is_ocr_garbage_claim(GARBLED)
    assert clean_learner_claim(OCR_INTRO) == ""
    assert not is_ocr_garbage_claim(
        "An acid tastes sour and turns blue litmus red in the laboratory."
    )


def test_junk_fragments_blocked():
    for term in ("EVIOUS", "CLASSES", "BITTER", "TASTES", "previous", "respectively"):
        assert is_junk_term(term), term


def test_chemistry_canonical_definitions():
    assert "sour" in canonical_definition("Acid").lower()
    assert "bitter" in canonical_definition("Bases").lower()
    assert "salt" in canonical_definition("Salts").lower()
    assert "litmus" in canonical_definition("Indicator").lower() or "colour" in canonical_definition(
        "Indicator"
    ).lower()


def test_question_grammar_for_plurals():
    assert question_what_is("Bases") == "What are bases? (1 mark)"
    assert question_what_is("Salts") == "What are salts? (1 mark)"
    assert "an acid" in question_what_is("Acid").lower()
    assert "baking soda" in question_what_is("Baking soda").lower()


def test_board_seeds_acids_pack_when_ocr_pollutes_claims():
    board = build_lesson_intelligence_board(
        clg={
            "topic": "Acids, Bases and Salts",
            "subject_key": "science",
            "facts": [{"text": OCR_INTRO}, {"text": GARBLED}],
            "core_concepts": ["EVIOUS", "CLASSES", "BITTER", "Acids"],
        }
    )
    names = [str(c.get("name") or "").lower() for c in board.get("concepts") or []]
    assert "evious" not in names
    assert "classes" not in names
    assert "bitter" not in names
    assert any(n in names for n in ("acid", "base", "salt", "indicator", "litmus"))
    claims = " ".join(board.get("verified_claims") or []).lower()
    assert "2chapter" not in claims
    assert "lear nt" not in claims


def test_canonical_lesson_teaches_real_chemistry_not_ocr():
    board = {
        "topic": "Acids, Bases and Salts",
        "subject": "science",
        "verified_claims": [
            OCR_INTRO,
            GARBLED,
            "In this Chapter, we will study the reactions of acids and bases.",
        ],
        "concepts": [
            {"name": "EVIOUS", "explanation": OCR_INTRO},
            {"name": "CLASSES", "explanation": OCR_INTRO},
            {"name": "Acids", "explanation": ""},
            {"name": "Bases", "explanation": ""},
        ],
        "misconceptions": [],
        "learning_goals": [],
        "examples": [],
        "assessment_objectives": [],
    }
    lesson = build_canonical_lesson(board)
    blob = " ".join(str(s.get("body") or "") + " " + str(s.get("title") or "") for s in lesson["sections"])
    low = blob.lower()
    assert "2chapter" not in low
    assert "lear nt" not in low
    assert "evious" not in low
    assert "one of the ideas taught" not in low
    assert "what are bases" in low or "what is a base" in low or "base" in low
    # Real teaching definitions must appear
    assert "litmus" in low or "sour" in low or "bitter" in low


def test_vocab_cards_reject_hollow_and_junk():
    items = normalize_vocab_items(
        [
            {"term": "EVIOUS", "definition": OCR_INTRO},
            {"term": "Salts", "definition": "Salts is one of the ideas taught in Acids, Bases."},
            {"term": "Baking soda", "definition": ""},
        ],
        topic="Acids, Bases and Salts",
        claims=[OCR_INTRO],
    )
    terms = {str(i["term"]).lower() for i in items}
    assert "evious" not in terms
    defs = " ".join(str(i.get("definition") or "") for i in items).lower()
    assert "one of the ideas taught" not in defs
    assert "2chapter" not in defs
    assert any("baking" in t for t in terms) or "baking soda" in defs
