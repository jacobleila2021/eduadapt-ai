"""Master Lesson Contract — one chemistry curriculum; presentation-only adaptations."""

from __future__ import annotations

from engines.lesson_composition_engine.canonical import (
    build_canonical_lesson,
    derive_presentation_adaptation,
    extract_essential_learning_core,
    freeze_canonical,
)
from engines.lesson_composition_engine.composer import compose_worksheet_from_clg
from engines.lesson_composition_engine.vocab_quality import (
    canonical_definition,
    clean_learner_claim,
    is_ocr_garbage_claim,
)


def test_acid_bank_includes_formulae():
    acid = canonical_definition("Acid")
    assert "HCl" in acid or "H⁺" in acid or "H+" in acid
    assert "H₂SO₄" in acid or "H2SO4" in acid or "sulphuric" in acid.lower()
    base = canonical_definition("Base")
    assert "OH" in base
    assert "NaOH" in base or "hydroxide" in base.lower()


def test_page_header_ocr_rejected():
    assert is_ocr_garbage_claim("Acids, Bases and Salts 19")
    assert "19" not in clean_learner_claim(
        "A salt forms in neutralisation. Acids, Bases and Salts 19 Which of these?"
    ) or clean_learner_claim(
        "A salt forms in neutralisation. Acids, Bases and Salts 19 Which of these?"
    ) == ""


def test_master_and_dyslexia_share_curriculum_depth():
    board = {
        "topic": "Acids, Bases and Salts",
        "subject": "science",
        "verified_claims": [],
        "concepts": [
            {"name": "Acid", "explanation": ""},
            {"name": "Base", "explanation": ""},
            {"name": "Salt", "explanation": ""},
        ],
        "misconceptions": [],
        "learning_goals": [],
        "examples": [],
        "assessment_objectives": [],
    }
    master = build_canonical_lesson(board)
    core = extract_essential_learning_core(master, board)
    frozen = freeze_canonical(master, core)
    dyslexia = derive_presentation_adaptation(frozen, core, "ld")
    master_blob = " ".join(str(s.get("body") or "") for s in master["sections"]).lower()
    dyslexia_blob = " ".join(str(s.get("body") or "") for s in dyslexia["sections"]).lower()
    assert "hcl" in master_blob or "h⁺" in master_blob or "hydrogen" in master_blob
    # Same curriculum tokens — presentation may reformat bullets/spacing.
    for token in ("acid", "base", "salt", "litmus"):
        assert token in master_blob and token in dyslexia_blob
    titles = " ".join(str(s.get("title") or "") for s in master["sections"])
    assert "What are Acids?" in titles or "Acid" in titles


def test_exam_short_answers_do_not_echo_question():
    sheet = compose_worksheet_from_clg(
        {
            "topic": "Acids, Bases and Salts",
            "subject_key": "science",
            "facts": [
                {"text": "You can also use synthetic indicators such as methyl orange and phenolphthalein to test for acids and bases."},
                {"text": "When the litmus solution is neither acidic nor basic, its colour is purple."},
                {"text": "Acids, Bases and Salts 19"},
            ],
            "core_concepts": [
                {"name": "Acid", "explanation": ""},
                {"name": "Base", "explanation": ""},
                {"name": "Salt", "explanation": ""},
            ],
        }
    )
    for row in sheet["short_answer"]:
        q = str(row.get("question") or "").lower()
        a = str(row.get("model_answer") or "").lower()
        assert "in your own words, explain this idea from the lesson:" not in q
        # Answer must not be a near-verbatim paste of a fact embedded in the question.
        if "explain this idea" in q:
            raise AssertionError("echo-style question should be gone")
        assert "acids, bases and salts 19" not in a
        assert len(a.split()) >= 6
    long_blob = " ".join(str(r.get("model_answer") or "") for r in sheet["long_answer"]).lower()
    assert "acids, bases and salts 19" not in long_blob
    assert "hcl" in long_blob or "salt" in long_blob or "neutral" in long_blob
