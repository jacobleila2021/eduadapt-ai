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
    # OCR sentence fragments must never become Lesson Wall titles
    assert normalize_wall_title("IN OTHER WORDS", idea="In other words is V = IR.") == ""
    assert normalize_wall_title("SOLUTION WE", idea="Solution We are given, I = 0.") == ""
    assert normalize_wall_title(
        "IF ONE END OF THE TUBE",
        idea="If one end of the tube is connected to a tank of water…",
    ) == ""
    assert normalize_wall_title("ITS SI UNIT", idea="Its SI unit is ohm.") == ""
    assert normalize_wall_title(
        "IN MANY PRACTICAL CASES IT",
        idea="In many practical cases it is necessary to increase current.",
    ) == ""
    assert is_junk_term("Can you name some metals that")
    assert is_junk_term("GOLD IS GOLD")
    assert is_junk_term("For example")
    assert is_junk_term("Extend")
    assert is_junk_term("In other words")
    assert is_junk_term("Solution We")
    assert is_junk_term("clouds")
    assert is_junk_term("plants")


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
        ans = str(row["model_answer"]).lower()
        # Focused: answer must centre on the asked concept, not dump the whole cycle.
        title = ""
        for card in wall:
            if card["title"].lower() in str(row["question"]).lower():
                title = card["title"].lower()
                break
        if title:
            assert title in ans
            # Near-duplicate vapour/vapor lines must not appear twice.
            assert ans.count("liquid water") <= 1


def test_water_cycle_diagram_is_canonical_only():
    stages = filter_diagram_stages(
        [
            "water cycle",
            "condensation",
            "precipitation",
            "collection",
            "clouds",
            "plants",
            "atmosphere",
            "oceans",
        ],
        topic="The Water Cycle",
        claims=["The water cycle moves water through evaporation and precipitation."],
        limit=6,
    )
    blob = " ".join(stages).lower()
    assert stages == [
        "Evaporation",
        "Condensation",
        "Precipitation",
        "Collection",
        "Transpiration",
    ]
    assert "clouds" not in blob
    assert "plants" not in blob
    assert "atmosphere" not in blob
    assert "oceans" not in blob
    assert "water cycle" not in blob


def test_magnetism_wall_and_wheel_reject_lab_ocr():
    from engines.lesson_composition_engine.dynamic_teaching_bank import ensure_wall_from_bank
    from engines.lesson_composition_engine.diagrams import build_concept_map_svg

    topic = "Magnetic Effects of Electric Current"
    junk = [
        {
            "title": "Take care that the cardboard",
            "idea": "Take care that the cardboard is fixed and does not slide up or down.",
        },
        {
            "title": "The wire XY",
            "idea": "The wire XY is kept perpendicular to the plane of paper.",
        },
        {
            "title": "Thus the magnetic field lines",
            "idea": "Thus the magnetic field lines are closed curves.",
        },
        {
            "title": "Theend pointing towards north",
            "idea": "Theend pointing towards north is called north seeking or north pole.",
        },
    ]
    wall = ensure_wall_from_bank(junk, [], topic=topic, min_cards=3)
    titles = " ".join(c["title"].lower() for c in wall)
    assert "cardboard" not in titles
    assert "wire xy" not in titles
    assert "thus the" not in titles
    assert any("magnetic" in c["title"].lower() or "field" in c["title"].lower() for c in wall)
    # Wheel must not orbit lab crumbs; hub must not be truncated "Magnetic Effects of"
    stages = filter_diagram_stages(
        ["Take care that the cardboard", "The wire XY", "Electric circuit", "Potential difference"],
        topic=topic,
        limit=6,
    )
    assert all("cardboard" not in s.lower() and "wire" not in s.lower() for s in stages)
    assert any("magnetic" in s.lower() or "solenoid" in s.lower() or "electromagnet" in s.lower() for s in stages)
    svg = build_concept_map_svg(topic, ["Take care that the cardboard", "The field", "Electric circuit"])
    low = svg.lower()
    assert "cardboard" not in low
    assert "the wire" not in low
    assert "magnetic field" in low
    assert "potential difference" not in low


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
    assert any(k in blob for k in ("metal", "malleab", "ductil", "lustre", "non-metal"))


def test_electricity_wall_rejects_ocr_fragments_and_seeds_bank():
    from engines.lesson_composition_engine.dynamic_teaching_bank import ensure_wall_from_bank

    junk_wall = [
        {
            "title": "IN OTHER WORDS",
            "idea": "In other words is V ∝ I (11.4) or V/I = constant = Ror V = IR (11.",
        },
        {
            "title": "SOLUTION WE",
            "idea": "Solution We are given, I = 0.",
        },
        {
            "title": "IF ONE END OF THE TUBE",
            "idea": "If one end of the tube is connected to a tank of water kept at a higher level.",
        },
    ]
    filled = ensure_wall_from_bank(junk_wall, [], topic="Electricity", min_cards=3)
    titles = {c["title"].lower() for c in filled}
    assert "in other words" not in titles
    assert "solution we" not in titles
    assert len(filled) >= 3
    assert any("current" in t or "ohm" in t or "resistance" in t or "circuit" in t for t in titles)
