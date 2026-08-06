"""Quality bar: teachable wall, deep 8-mark answers, no junk vocab/diagram nodes."""

from __future__ import annotations

from engines.lesson_composition_engine.lesson_wall import (
    clean_wall_idea,
    dedupe_lesson_wall,
    normalize_wall_title,
    wall_long_answers,
    wall_vocab_terms,
)
from engines.lesson_composition_engine.vocab_quality import (
    filter_diagram_stages,
    is_junk_term,
)


def test_junk_question_titles_rejected():
    assert normalize_wall_title("Can you name some metals that") == ""
    assert normalize_wall_title("Do you know why these metals") == ""
    assert normalize_wall_title("For example") == ""
    assert normalize_wall_title("This property") == ""
    assert normalize_wall_title("Reprint 2026-27") == ""
    assert normalize_wall_title(
        "GOLD IS GOLD", idea="Gold is Gold is the most ductile metal."
    ) == "Gold"
    assert normalize_wall_title("Understanding Evaporation") == "Evaporation"
    assert is_junk_term("Can you name some metals that")
    assert is_junk_term("GOLD IS GOLD")
    assert is_junk_term("For example")
    assert is_junk_term("Extend")


def test_clean_wall_idea_fixes_gold_is_gold():
    fixed = clean_wall_idea("Gold is Gold is the most ductile metal.")
    assert "gold is gold is" not in fixed.lower()
    assert "ductile" in fixed.lower()


def test_dedupe_drops_question_wall_cards():
    wall = dedupe_lesson_wall(
        [
            {
                "title": "Can you name some metals that",
                "idea": "Can you name some metals that are used for making cooking vessels?",
            },
            {
                "title": "Malleability",
                "idea": "Malleability is the property that allows metals to be hammered into thin sheets.",
            },
            {
                "title": "Ductility",
                "idea": "Ductility is the property that allows metals to be drawn into thin wires.",
            },
            {
                "title": "Lustre",
                "idea": "Lustre is the shiny appearance of a clean metal surface.",
            },
        ]
    )
    titles = {c["title"].lower() for c in wall}
    assert "can you name some metals that" not in titles
    assert "malleability" in titles


def test_eight_mark_answers_are_multi_sentence():
    wall = [
        {
            "title": "Evaporation",
            "idea": "Evaporation is when liquid water turns into water vapour and rises into the air.",
        },
        {
            "title": "Condensation",
            "idea": "Condensation is when water vapour cools and changes back into tiny liquid droplets.",
        },
        {
            "title": "Precipitation",
            "idea": "Precipitation is water that falls from clouds as rain, snow, sleet, or hail.",
        },
    ]
    long_q = wall_long_answers(wall, topic="The Water Cycle", limit=3)
    assert long_q
    for row in long_q:
        assert "from the lesson" not in row["question"].lower()
        assert len(str(row["model_answer"]).split()) >= 24
        assert row["marks"] == 8


def test_vocab_terms_skip_junk_wall_titles():
    terms = wall_vocab_terms(
        [
            {
                "title": "For example",
                "idea": "For example is (i) All metals except mercury exist as solids.",
            },
            {
                "title": "Malleability",
                "idea": "Malleability is the property that allows metals to be hammered into thin sheets.",
            },
        ]
    )
    names = {t["term"].lower() for t in terms}
    assert "for example" not in names
    assert "malleability" in names


def test_metals_diagram_does_not_seed_acid_base():
    stages = filter_diagram_stages(
        ["Gold", "Acid", "Base", "Malleability", "Ductility"],
        topic="Metals and Non-metals",
        claims=["Metals are shiny and malleable.", "Gold is the most ductile metal."],
        limit=6,
    )
    blob = " ".join(stages).lower()
    assert "acid" not in blob
    assert "base" not in blob
    assert any(k in blob for k in ("metal", "malleab", "ductil", "lustre", "non-metal", "gold"))
