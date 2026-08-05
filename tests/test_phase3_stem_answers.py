"""Phase 3 — STEM via router; Practice/Exam answers from EngineResult."""

from __future__ import annotations

from engines.lesson_composition_engine.canonical import build_canonical_lesson
from engines.lesson_composition_engine.composer import compose_worksheet_from_clg
from engines.lesson_pipeline import (
    format_engine_answer,
    looks_like_computable_stem,
    match_artifact_to_prompt,
    process_lesson_stem,
    verified_or_wall_answer,
)
from engines.safe_math import validate_math_expression


def test_textbook_math_validates_with_implicit_multiply():
    v = validate_math_expression("x^2 - 5x + 6 = 0", allow_equation=True)
    assert v.ok, v.reason
    assert "5*x" in v.normalized


def test_process_lesson_stem_routes_balance_and_solve():
    text = (
        "Balance: H2 + O2 -> H2O\n"
        "Solve x^2 - 5x + 6 = 0\n"
        "Evaporation is when liquid water turns into vapour.\n"
    )
    out = process_lesson_stem(text, topic="STEM")
    kinds = {a.get("task_kind") for a in out.get("artifacts") or [] if a.get("ok")}
    assert "balance_equation" in kinds
    assert "solve_math" in kinds


def test_format_and_match_engine_answer():
    stem = process_lesson_stem("Balance: H2 + O2 -> H2O\n", topic="Chem")
    arts = stem["artifacts"]
    assert arts
    text = format_engine_answer(arts[0])
    assert "balanced" in text.lower() or "h2o" in text.lower()
    matched = match_artifact_to_prompt("Balance the equation H2 + O2 -> H2O", arts)
    assert matched and matched.get("ok")
    policy = verified_or_wall_answer(
        "Balance H2 + O2 -> H2O", artifacts=arts, wall_prose="Water forms."
    )
    assert policy["source"] == "engine_result"
    assert policy["text"]


def test_computable_stem_without_artifact_omits_invention():
    assert looks_like_computable_stem("Calculate the current when V = 12 V and R = 4 ohm")
    policy = verified_or_wall_answer(
        "Calculate the current when V = 12 V and R = 4 ohm",
        artifacts=[],
        wall_prose="Current is the flow of charge.",
    )
    assert policy["omitted"] is True


def test_canonical_practice_includes_engine_answer():
    stem = process_lesson_stem("Balance: H2 + O2 -> H2O\n", topic="Chemistry")
    page = build_canonical_lesson(
        {
            "topic": "Chemical Reactions",
            "verified_claims": [
                "A chemical reaction rearranges atoms into new substances.",
            ],
            "concepts": [{"name": "Chemical reaction", "explanation": "Atoms rearrange."}],
            "source_text": "Balance: H2 + O2 -> H2O\n",
            "stem_artifacts": stem["artifacts"],
        },
        stem_artifacts=stem["artifacts"],
    )
    practice = next(
        (s for s in page.get("sections") or [] if s.get("role") == "practice_question"),
        {},
    )
    body = str(practice.get("body") or "").lower()
    assert "balance" in body or "h2" in body
    assert "2h2o" in body.replace(" ", "") or "balanced" in body


def test_worksheet_short_answers_use_engine_result():
    stem = process_lesson_stem("Balance: H2 + O2 -> H2O\n", topic="Chemistry")
    sheet = compose_worksheet_from_clg(
        {
            "topic": "Chemical Reactions",
            "core_concepts": [{"name": "Reaction", "explanation": "Atoms rearrange."}],
            "claim_texts": ["A chemical reaction rearranges atoms."],
            "assessment_outcomes": [
                {"prompt": "Balance H2 + O2 -> H2O", "marks": 3, "question_type": "numerical"}
            ],
            "facts": [],
            "vocabulary": [],
        },
        stem_artifacts=stem["artifacts"],
    )
    short = sheet.get("short_answer") or []
    assert any(str(r.get("source") or "") == "engine_result" for r in short)
    blob = " ".join(str(r.get("model_answer") or "") for r in short).lower()
    assert "balanced" in blob or "2h2o" in blob.replace(" ", "")
