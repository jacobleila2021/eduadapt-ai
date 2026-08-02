"""R10–R11: dynamic teaching bank from any upload (not only hand banks)."""

from __future__ import annotations

from engines.lesson_composition_engine.canonical import build_canonical_lesson
from engines.lesson_composition_engine.composer import compose_vocabulary_from_clg
from engines.lesson_composition_engine.dynamic_teaching_bank import (
    build_dynamic_teaching_bank,
    definition_from_dynamic_bank,
    extract_definitional_pairs,
)
from engines.lesson_composition_engine.intelligence_board import (
    build_lesson_intelligence_board,
)


PHOTOSYNTHESIS = """
Photosynthesis

Photosynthesis is the process by which green plants make food using sunlight,
carbon dioxide and water.

Chlorophyll is the green pigment in leaves that absorbs light energy.

Stomata are tiny pores on the leaf surface that allow gas exchange.

Glucose is the sugar produced during photosynthesis and used by the plant for energy.

QUESTIONS
1. What is photosynthesis?
2. Name the pigment that absorbs light energy.
3. What are stomata?
"""


def test_extract_definitional_pairs_from_prose():
    pairs = extract_definitional_pairs(PHOTOSYNTHESIS)
    terms = {t.lower() for t, _ in pairs}
    assert "photosynthesis" in terms or "chlorophyll" in terms
    assert any(len(d.split()) >= 5 for _, d in pairs)


def test_build_dynamic_bank_bankless_topic():
    bank = build_dynamic_teaching_bank(
        topic="Photosynthesis",
        source_text=PHOTOSYNTHESIS,
        claims=[
            "Photosynthesis is the process by which green plants make food.",
            "Chlorophyll is the green pigment in leaves that absorbs light energy.",
        ],
    )
    assert len(bank) >= 2
    assert definition_from_dynamic_bank("Chlorophyll", bank)
    blob = " ".join(r["definition"].lower() for r in bank)
    assert "for performing" not in blob
    assert "activity" not in blob or "chlorophyll" in blob


def test_intelligence_board_attaches_teaching_bank():
    board = build_lesson_intelligence_board(
        {
            "topic": "Photosynthesis",
            "source_text": PHOTOSYNTHESIS,
            "facts": [{"text": "Photosynthesis is the process by which green plants make food."}],
            "claim_texts": [
                "Photosynthesis is the process by which green plants make food using sunlight.",
                "Chlorophyll is the green pigment in leaves that absorbs light energy.",
                "Stomata are tiny pores on the leaf surface that allow gas exchange.",
            ],
            "core_concepts": [{"name": "Photosynthesis"}, {"name": "Chlorophyll"}],
            "assessment_outcomes": [{"prompt": "What is photosynthesis?"}],
        }
    )
    bank = board.get("teaching_bank") or []
    assert bank, "board must attach a dynamic teaching bank for bankless topics"
    assert board.get("engine_contributions", {}).get("dynamic_teaching_bank") is True


def test_master_uses_dynamic_bank_explanations():
    board = build_lesson_intelligence_board(
        {
            "topic": "Photosynthesis",
            "source_text": PHOTOSYNTHESIS,
            "claim_texts": [
                "Photosynthesis is the process by which green plants make food using sunlight.",
                "Chlorophyll is the green pigment in leaves that absorbs light energy.",
                "Stomata are tiny pores on the leaf surface that allow gas exchange.",
            ],
            "core_concepts": [
                {"name": "Chlorophyll", "explanation": ""},
                {"name": "Stomata", "explanation": ""},
            ],
        }
    )
    page = build_canonical_lesson(board)
    blob = str(page).lower()
    assert "chlorophyll" in blob
    assert "pigment" in blob or "stomata" in blob


def test_vocab_seeds_from_teaching_bank():
    bank = build_dynamic_teaching_bank(
        topic="Photosynthesis",
        source_text=PHOTOSYNTHESIS,
        claims=[
            "Chlorophyll is the green pigment in leaves that absorbs light energy.",
            "Stomata are tiny pores on the leaf surface that allow gas exchange.",
        ],
    )
    page = compose_vocabulary_from_clg(
        {
            "topic": "Photosynthesis",
            "source_text": PHOTOSYNTHESIS,
            "teaching_bank": bank,
            "claim_texts": [
                "Chlorophyll is the green pigment in leaves that absorbs light energy.",
            ],
            "core_concepts": [{"name": "Chlorophyll"}, {"name": "Stomata"}],
            "vocabulary": [],
            "facts": [],
        }
    )
    wall = page.get("word_wall") or []
    terms = {str(w.get("term") or "").lower() for w in wall}
    assert terms & {"chlorophyll", "stomata", "photosynthesis", "glucose"}
