"""Exam worksheet — CBSE stems, matched answers, no clone templates."""

from __future__ import annotations

from engines.lesson_composition_engine.composer import (
    _answer_mentions_term,
    _matched_answer_for_term,
    _short_answer_prompt,
    compose_worksheet_from_clg,
)


WATER = {
    "topic": "The Water Cycle",
    "subject_key": "science",
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
        {"name": "Transpiration", "explanation": "Transpiration is water vapour leaving plant leaves."},
        {"name": "Clouds", "explanation": ""},
        {"name": "Plants", "explanation": ""},
    ],
    "assessment_outcomes": [],
    "vocabulary": [
        {"term": "Evaporation"},
        {"term": "Condensation"},
        {"term": "Precipitation"},
        {"term": "Collection"},
        {"term": "Transpiration"},
    ],
}


def test_short_prompts_are_what_is_or_define_not_explain_clone():
    prompts = [_short_answer_prompt("Evaporation", index=i)[0].lower() for i in range(8)]
    assert any(p.startswith("what is") for p in prompts)
    assert any(p.startswith("define") for p in prompts)
    assert not any("give its meaning and one clear example" in p for p in prompts)
    assert not any(p.startswith("explain ") for p in prompts)


def test_matched_answer_never_swaps_clouds_for_evaporation():
    assert (
        _matched_answer_for_term(
            "Clouds",
            pool=[
                "Evaporation is when liquid water turns into water vapour.",
                "Transpiration adds water vapour from plants.",
            ],
        )
        == ""
    )
    ans = _matched_answer_for_term(
        "Evaporation",
        pool=["Evaporation is when liquid water turns into water vapour."],
        want_example=True,
    )
    assert _answer_mentions_term(ans, "Evaporation")
    assert "example" in ans.lower() or "puddle" in ans.lower()


def test_worksheet_part_a_and_d_quality():
    sheet = compose_worksheet_from_clg(
        WATER,
        vocabulary={
            "word_wall": [
                {
                    "term": "Evaporation",
                    "definition": "Evaporation is when liquid water turns into vapour.",
                },
                {
                    "term": "Condensation",
                    "definition": "Condensation is when vapour cools into droplets.",
                },
                {
                    "term": "Precipitation",
                    "definition": "Precipitation is rain, snow, sleet, or hail.",
                },
            ]
        },
    )
    short = sheet.get("short_answer") or []
    assert len(short) >= 4
    blob_q = " ".join(str(r.get("question") or "") for r in short).lower()
    assert "give its meaning and one clear example" not in blob_q
    assert "explain clouds" not in blob_q
    assert "explain plants" not in blob_q
    for row in short:
        q = str(row.get("question") or "").lower()
        a = str(row.get("model_answer") or "")
        assert a.strip()
        if q.startswith(("what is", "define", "state the meaning")):
            assert len(a.split()) >= 6
            # Answer must not be an unrelated stage when a stage is asked.
            if "evaporation" in q:
                assert "evaporat" in a.lower()
            if "condensation" in q:
                assert "condens" in a.lower()

    vocab_q = sheet.get("vocab_questions") or []
    assert vocab_q, "Part D must have definition questions"
    vblob = " ".join(str(r.get("question") or "") for r in vocab_q).lower()
    assert "write one correct sentence that uses the term" not in vblob
    assert "what is" in vblob or "define" in vblob
    for row in vocab_q:
        assert _answer_mentions_term(
            str(row.get("model_answer") or ""),
            # pull display term roughly
            str(row.get("question") or "")
            .replace("What is ", "")
            .replace("Define ", "")
            .replace("the ", "")
            .strip(" ?."),
        ) or len(str(row.get("model_answer") or "").split()) >= 5
