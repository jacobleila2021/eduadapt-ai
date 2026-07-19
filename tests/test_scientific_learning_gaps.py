"""Unit tests for Phase-3 scientific learning gap fills."""

from __future__ import annotations

from pathlib import Path

from engines.mathematics.solver import solve
from engines.lesson_pipeline import _is_explicit_question_line
from engines.router import route
from engines.types import TaskKind, ToolTask
from knowledge.chapter_cache import (
    approve_chapter_package,
    factual_fingerprint,
    load_approved_package,
)
from knowledge.question_bank import match_exam_bundle, load_official_items
from knowledge.service import prepare_knowledge_for_lesson


def test_calculus_diff_and_integrate():
    d = solve("differentiate x**2")
    assert d.ok
    assert "2*x" in str(d.payload.get("exact"))
    assert d.payload.get("steps")
    integ = solve("integrate x")
    assert integ.ok
    assert integ.payload.get("operation") == "integrate"


def test_statistics_engine():
    r = route(ToolTask(kind=TaskKind.STATISTICS, payload={"raw": "mean of 2 4 6 8"}))
    assert r.ok
    exact = r.payload.get("exact") or {}
    assert exact.get("mean") == 5.0
    assert exact.get("n") == 4


def test_chapter_cache_roundtrip(tmp_path, monkeypatch):
    import knowledge.chapter_cache as cc

    monkeypatch.setattr(cc, "APPROVED_DIR", tmp_path)
    arts = [
        {
            "task_kind": "solve_math",
            "engine_id": "sympy",
            "latex": "x=4",
            "deterministic": True,
            "payload": {"exact": "[4]"},
        }
    ]
    fp = factual_fingerprint("Cell", arts, ["cite1"])
    pkg = approve_chapter_package(
        topic="Cell",
        artifacts=arts,
        preferred_visuals=[],
        knowledge={"citations": ["cite1"], "subject": "Science"},
    )
    assert pkg["fingerprint"] == fp
    loaded = load_approved_package(fp)
    assert loaded and loaded["approved"] is True


def test_exam_bundle_has_typed_sources():
    items = load_official_items()
    assert any(it.question_type == "hots" for it in items)
    assert any("Competency" in it.source for it in items)
    bundle = match_exam_bundle("Cell Structure", ["cell", "vacuole"], limit_per_type=2)
    assert "hots" in bundle
    assert "competency" in bundle


def test_question_bank_fails_closed_for_unrelated_lesson():
    bundle = match_exam_bundle(
        "The Water Cycle",
        ["evaporation", "condensation", "precipitation", "collection"],
        limit_per_type=2,
    )
    assert all(not items for items in bundle.values())


def test_fixed_class8_pilot_is_skipped_for_other_grades():
    knowledge = prepare_knowledge_for_lesson(
        "Grade Level: 6 | Subject: Earth Science\nThe water cycle includes evaporation.",
        {
            "topic": "The Water Cycle",
            "grade_level": "Grade 6",
            "vocabulary_terms": ["evaporation", "condensation"],
        },
    )
    assert knowledge["scope_matched"] is False
    assert knowledge["rag_hits"] == []
    assert knowledge["official_mcqs"] == []
    assert knowledge["exam_bundle"] == {}


def test_lesson_objectives_are_not_routed_as_questions():
    assert not _is_explicit_question_line(
        "Students will explain how water changes state during the water cycle."
    )
    assert not _is_explicit_question_line(
        "Success criteria: explain each process using complete sentences."
    )
    assert _is_explicit_question_line("Q1. Explain how evaporation occurs.")
    assert _is_explicit_question_line("Why does condensation form clouds?")


def test_water_cycle_uses_rich_deterministic_visual():
    from flowchart_builder import build_vocabulary_visual_svg

    svg = build_vocabulary_visual_svg(
        {
            "topic": "The Water Cycle",
            "picture_words": [
                {"term": "Evaporation"},
                {"term": "Condensation"},
                {"term": "Precipitation"},
                {"term": "Collection"},
            ],
        }
    )
    assert svg.startswith("<svg")
    for label in ("Evaporation", "Condensation", "Precipitation", "Collection"):
        assert label in svg
    assert "linearGradient" in svg
    assert "feDropShadow" in svg


def test_biology_pack_exists():
    from knowledge.biology_figures import match_biology_figures

    figs = match_biology_figures("plant cell chloroplast", topic="Cell", limit=1)
    assert figs
    assert Path(figs[0]["path"]).is_file()


def test_curated_figures_do_not_leak_into_acids_lesson():
    from knowledge.biology_figures import match_biology_figures

    lesson = (
        "Acids, Bases and Salts. Acids react with metals and bases neutralise "
        "acids. A normal laboratory activity may mention area, pressure, "
        "force, reflection, or a flame without teaching those topics."
    )
    assert match_biology_figures(lesson, topic="Acids, Bases and Salts") == []


def test_chapter_cache_fingerprint_is_source_bound():
    assert factual_fingerprint("Science", [], [], "source-a") != factual_fingerprint(
        "Science", [], [], "source-b"
    )
