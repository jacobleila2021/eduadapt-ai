"""Water Cycle — lesson wall, diagram share, vocab, no key-word/Model chrome."""

from __future__ import annotations

from audio_learning import build_narration, _clean_for_speech
from engines.lesson_composition_engine.canonical import (
    build_canonical_lesson,
    derive_presentation_adaptation,
    extract_essential_learning_core,
    freeze_canonical,
)
from engines.lesson_composition_engine.composer import (
    _diagrams_from_board,
    compose_vocabulary_from_clg,
)
from engines.lesson_composition_engine.intelligence_board import (
    build_lesson_intelligence_board,
)


SOURCE = """
The Water Cycle

The water cycle is the continuous movement of water on, above, and below Earth's surface.
Evaporation is when liquid water turns into water vapour and rises into the air.
Condensation is when water vapour cools and changes back into tiny liquid droplets.
Precipitation is water that falls from clouds as rain, snow, sleet, or hail.
Collection is when water gathers in rivers, lakes, oceans, and groundwater.
Transpiration is when plants release water vapour into the air from their leaves.

QUESTIONS
1. What is evaporation?
2. Explain condensation.
3. What is precipitation?
"""


def _board():
    return build_lesson_intelligence_board(
        {
            "topic": "The Water Cycle",
            "source_text": SOURCE,
            "claim_texts": [
                "The water cycle is the continuous movement of water on, above, and below Earth's surface.",
                "Evaporation is when liquid water turns into water vapour and rises into the air.",
                "Condensation is when water vapour cools and changes back into tiny liquid droplets.",
                "Precipitation is water that falls from clouds as rain, snow, sleet, or hail.",
                "Collection is when water gathers in rivers, lakes, oceans, and groundwater.",
            ],
            "core_concepts": [
                {"name": "Evaporation"},
                {"name": "Condensation"},
                {"name": "Precipitation"},
                {"name": "Collection"},
            ],
            "facts": [],
            "vocabulary": [],
        }
    )


def test_primary_diagram_is_water_cycle_not_generic():
    board = _board()
    primary, _secondary = _diagrams_from_board(board, {"topic": "The Water Cycle"})
    low = primary.lower()
    assert "evaporat" in low or "sun" in low or "collect" in low
    assert "phenomenon" not in low and "explore" not in low


def test_ell_has_no_key_word_or_model_chrome():
    board = _board()
    page = build_canonical_lesson(board)
    core = extract_essential_learning_core(page, board)
    frozen = freeze_canonical(page, core)
    ell = derive_presentation_adaptation(frozen, core, "ell")
    blob = str(ell).lower()
    assert "(key word)" not in blob
    assert "important words:" not in blob
    assert "model:" not in blob
    assert "evaporation" in blob


def test_vocab_uses_water_cycle_bank_not_clone_defs():
    page = compose_vocabulary_from_clg(
        {
            "topic": "The Water Cycle",
            "source_text": SOURCE,
            "claim_texts": [
                "The water cycle is the continuous movement of water among theatmosphere, land, and oceans.",
                "Evaporation is when liquid water turns into water vapour.",
            ],
            "core_concepts": [
                {"name": "Atmosphere"},
                {"name": "Oceans"},
                {"name": "Evaporation"},
                {"name": "Condensation"},
            ],
            "vocabulary": [],
            "facts": [],
        }
    )
    wall = page.get("word_wall") or []
    terms = {str(w.get("term") or "").lower(): str(w.get("definition") or "") for w in wall}
    assert "evaporation" in terms
    # Wrong recycled blurb must not become Atmosphere/Oceans cards.
    for bad in ("atmosphere", "oceans"):
        if bad in terms:
            assert "continuous movement" not in terms[bad].lower()
    defs = list(terms.values())
    # Distinct meanings — not the same sentence on every card.
    assert len(set(d.lower() for d in defs)) >= min(3, len(defs))


def test_reading_matches_lesson_points_no_duplicates():
    board = _board()
    page = build_canonical_lesson(board)
    speech = build_narration(page, "standard")
    low = speech.lower()
    assert "(key word)" not in low
    assert "important words" not in low
    assert "model answer" not in low
    assert "evaporation" in low
    # Near-duplicate paraphrase should not appear twice.
    assert low.count("liquid water turns into water vapour") <= 1
    assert "theenergy" not in _clean_for_speech("theenergy theatmosphere theentire")
    assert "the energy" in _clean_for_speech("theenergy theatmosphere theentire")
