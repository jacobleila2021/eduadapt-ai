"""v4 lesson quality — diagram stage validation + Q&A parse for tabs."""

from __future__ import annotations

from engines.lesson_composition_engine.vocab_quality import filter_diagram_stages, is_junk_term
from structured_renderers import _parse_qa_pairs


def test_faucets_never_become_diagram_stages():
    stages = filter_diagram_stages(
        ["condensation", "faucets", "clouds", "precipitation", "collection", "puddles"],
        topic="The Water Cycle",
        claims=[
            "Evaporation happens when the sun heats water.",
            "Condensation forms clouds when water vapour cools.",
            "Precipitation returns water as rain.",
            "Collection gathers water in rivers and lakes.",
        ],
    )
    low = {s.lower() for s in stages}
    assert "faucets" not in low
    assert "clouds" not in low  # warm-up noun, not a process stage
    assert "puddles" not in low
    assert "condensation" in low
    assert "precipitation" in low
    assert "collection" in low


def test_faucet_is_junk_term():
    assert is_junk_term("faucets")
    assert is_junk_term("faucet")


def test_parse_qa_pairs_from_collapsed_paragraph():
    body = (
        "1. What is evaporation? (1 mark) Answer: Evaporation is liquid water becoming vapour. "
        "2. What is condensation? (1 mark) Answer: Condensation forms tiny droplets."
    )
    pairs = _parse_qa_pairs(body)
    assert len(pairs) >= 2
    assert pairs[0]["n"] == 1
    assert "evaporation" in pairs[0]["question"].lower()
    assert "Answer" not in pairs[0]["answer"]
    assert "vapour" in pairs[0]["answer"].lower() or "vapor" in pairs[0]["answer"].lower()
    assert pairs[1]["n"] == 2


def test_parse_qa_pairs_multiline():
    body = "1. Explain force. (3 marks)\nAnswer: Force is a push or a pull.\n\n2. Define pressure. (2 marks)\nAnswer: Force on unit area.\n"
    pairs = _parse_qa_pairs(body)
    assert len(pairs) == 2
    assert pairs[0]["marks"] == 3
    assert "push" in pairs[0]["answer"].lower()
