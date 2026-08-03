"""Lesson Wall is the single source of truth for vocab, exam, reading, diagrams."""

from __future__ import annotations

from audio_learning import build_narration
from engines.lesson_composition_engine.composer import compose_adaptations_from_clg
from engines.lesson_composition_engine.lesson_wall import (
    extract_lesson_wall,
    wall_long_answers,
    wall_vocab_terms,
)


CLG = {
    "topic": "The Water Cycle",
    "subject_key": "science",
    "source_text": """
The Water Cycle
The water cycle is the continuous movement of water on, above, and below Earth's surface.
Evaporation is when liquid water turns into water vapour and rises into the air.
Condensation is when water vapour cools and changes back into tiny liquid droplets.
Precipitation is water that falls from clouds as rain, snow, sleet, or hail.
Collection is when water gathers in rivers, lakes, oceans, and groundwater.
Transpiration is when plants release water vapour into the air from their leaves.
""",
    "claim_texts": [
        "The water cycle is the continuous movement of water on, above, and below Earth's surface.",
        "Evaporation is when liquid water turns into water vapour and rises into the air.",
        "Condensation is when water vapour cools and changes back into tiny liquid droplets.",
        "Precipitation is water that falls from clouds as rain, snow, sleet, or hail.",
        "Collection is when water gathers in rivers, lakes, oceans, and groundwater.",
        "Transpiration is when plants release water vapour into the air from their leaves.",
    ],
    "core_concepts": [
        {"name": "Evaporation", "explanation": "Evaporation is when liquid water turns into water vapour."},
        {"name": "Condensation", "explanation": "Condensation is when water vapour cools into droplets."},
        {"name": "Precipitation", "explanation": "Precipitation is rain, snow, sleet, or hail."},
        {"name": "Collection", "explanation": "Collection is water gathering in rivers and oceans."},
    ],
    "facts": [],
    "vocabulary": [],
    "assessment_outcomes": [],
}


def test_wall_drives_vocab_exam_reading_and_diagram():
    out = compose_adaptations_from_clg(CLG)
    wall = out.get("_lesson_wall") or []
    assert len(wall) >= 3, "Master lesson must produce a Lesson Wall"

    # Every student adaptation carries the same wall + domain diagram.
    for vid in ("standard", "ell", "parent", "visual", "auditory", "ld"):
        page = out.get(vid) or {}
        assert page.get("lesson_wall"), f"{vid} missing lesson_wall"
        svg = (
            str(page.get("svg_diagram") or "")
            + str(page.get("concept_map_svg") or "")
            + str((page.get("diagram_package") or {}).get("svg") or "")
        )
        assert "<svg" in svg.lower(), f"{vid} missing teaching diagram"
        assert "evaporat" in svg.lower() or "sun" in svg.lower() or "collect" in svg.lower()

    # Vocabulary definitions come from wall teaching text.
    vocab = out.get("vocabulary") or {}
    wall_blob = " ".join(str(c.get("idea") or "") for c in wall).lower()
    vocab_blob = " ".join(
        str(w.get("definition") or "") + " " + str(w.get("lesson_context") or "")
        for w in (vocab.get("word_wall") or [])
    ).lower()
    assert "evaporation" in vocab_blob
    assert any(token in vocab_blob for token in ("vapour", "vapor", "condens", "precipitat"))
    assert vocab.get("svg_diagram") or vocab.get("concept_map_svg")

    # 8-mark answers are wall text (source=lesson_wall).
    sheet = out.get("worksheet") or {}
    long_q = sheet.get("long_answer") or []
    assert long_q, "Exam worksheet must have Part B long answers from the wall"
    assert any(str(q.get("source") or "") == "lesson_wall" for q in long_q)
    for q in long_q:
        ans = str(q.get("model_answer") or "").lower()
        assert len(ans.split()) >= 8
        # Answer should reuse wall teaching language, not empty filler.
        assert "these points show what" not in ans

    # Reading voice = wall content.
    speech = build_narration(out["standard"], "standard").lower()
    assert "evaporation" in speech or "water cycle" in speech
    assert "(key word)" not in speech


def test_wall_helpers_extract_vocab_and_long_answers():
    lesson = {
        "sections": [
            {
                "role": "introduction",
                "title": "The Water Cycle",
                "body": (
                    "The water cycle is the continuous movement of water on, above, "
                    "and below Earth's surface."
                ),
            },
            {
                "role": "concept",
                "title": "Evaporation and Transpiration",
                "body": (
                    "Evaporation is when liquid water turns into water vapour. "
                    "Transpiration is when plants release water vapour from leaves."
                ),
            },
            {
                "role": "common_misconception",
                "title": "Common Mistakes to Avoid",
                "body": "Do not confuse evaporation with condensation.",
            },
        ]
    }
    wall = extract_lesson_wall(lesson)
    assert len(wall) >= 2
    terms = wall_vocab_terms(wall, topic="The Water Cycle")
    term_names = {t["term"].lower() for t in terms}
    assert "evaporation" in term_names or "evaporation and transpiration" in term_names
    long_q = wall_long_answers(wall, topic="The Water Cycle")
    assert long_q
    assert all(q["marks"] == 8 for q in long_q)
    assert all("common mistakes" not in q["question"].lower() for q in long_q)
