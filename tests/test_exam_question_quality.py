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


def test_statistics_artifact_not_injected_into_electricity_exam():
    """STEM statistics noise must never appear as Show Answer in science lessons."""
    sheet = compose_worksheet_from_clg(
        {
            "topic": "Electricity",
            "subject_key": "science",
            "claim_texts": [
                "Electric current is the rate of flow of electric charge through a conductor.",
                "Resistance is the property of a conductor that opposes current. Its SI unit is ohm.",
            ],
            "core_concepts": [
                {
                    "name": "Electric current",
                    "explanation": "Electric current is the rate of flow of charge.",
                },
                {
                    "name": "Resistance",
                    "explanation": "Resistance opposes current; SI unit is ohm.",
                },
                {
                    "name": "Ohm's law",
                    "explanation": "Ohm's law: V = IR at constant temperature.",
                },
            ],
            "assessment_outcomes": [],
            "vocabulary": [{"term": "Electric current"}, {"term": "Resistance"}],
            "stem_artifacts": [
                {
                    "ok": True,
                    "task_kind": "statistics",
                    "payload": {
                        "input": "[12, 15, 14, 10, 18, 15, 11]",
                        "result": {
                            "mean": 13.57,
                            "median": 14.0,
                            "mode": 15.0,
                        },
                    },
                }
            ],
        },
        vocabulary={
            "word_wall": [
                {
                    "term": "Electric current",
                    "definition": "Electric current is the rate of flow of charge.",
                }
            ]
        },
        stem_artifacts=[
            {
                "ok": True,
                "task_kind": "statistics",
                "payload": {
                    "input": "[12, 15, 14, 10, 18, 15, 11]",
                    "result": {"mean": 13.57, "median": 14.0, "mode": 15.0},
                },
            }
        ],
    )
    blob = " ".join(
        f"{r.get('question')} {r.get('model_answer')}"
        for r in (sheet.get("short_answer") or [])
    ).lower()
    assert "median" not in blob
    assert "13.57" not in blob
    assert "iqr" not in blob
    assert "exact result" not in blob
    assert "standard deviation" not in blob
    assert "solve:" not in blob or "ohm" in blob  # no stats Solve: stems
