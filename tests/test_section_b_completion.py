"""Regression tests for Section B completion."""

from __future__ import annotations

from engines.geometry.geogebra import build_geogebra, parse_geometry_kind
from engines.mathematics.advanced import try_advanced_math
from engines.mathematics.solver import solve
from engines.qa.pipeline import validate_lesson_package, _flesch_kincaid_grade
from engines.router import route
from engines.types import TaskKind, ToolTask
from knowledge.service import inject_exam_practice_into_lessons
from agents.orchestration import AGENT_ROSTER, AloraOrchestrator


def test_limits_and_matrix():
    lim = try_advanced_math("limit x->0 of sin(x)/x")
    assert lim and lim.ok
    mat = try_advanced_math("matrix [[1,2],[3,4]] determinant")
    assert mat and mat.ok


def test_calculus_still_works():
    assert solve("differentiate x**3").ok


def test_stats_regression():
    r = route(
        ToolTask(
            kind=TaskKind.STATISTICS,
            payload={"raw": "regression 1 2 2 4 3 5 4 7"},
        )
    )
    assert r.ok
    assert "regression" in (r.payload.get("exact") or {})


def test_geogebra_expanded():
    assert parse_geometry_kind("draw an ellipse") == "ellipse"
    g = build_geogebra("parabola")
    assert g.ok
    assert g.payload.get("iframe_url")
    assert g.payload.get("commands")


def test_exam_inject():
    knowledge = {
        "exam_bundle": {
            "hots": [
                {
                    "source": "HOTS",
                    "question": "Why vacuoles?",
                    "official_answer": "turgor",
                    "marks": 3,
                    "bloom": "analyze",
                }
            ]
        }
    }
    adaptations = {
        "standard": {
            "big_idea": "Cells",
            "sections": [{"title": "Intro", "body": "Plant cells have walls."}],
        }
    }
    out = inject_exam_practice_into_lessons(adaptations, knowledge)
    titles = [s["title"] for s in out["standard"]["sections"]]
    assert any("Exam Practice" in t for t in titles)


def test_reading_level_and_qa_scorecard():
    grade = _flesch_kincaid_grade(
        "The mitochondrion is the powerhouse of the cell. " * 20
    )
    assert grade is not None
    qa = validate_lesson_package(
        artifacts=[],
        preferred_visuals=[],
        knowledge={"subject": "math"},
        adaptations={
            "standard": {
                "big_idea": "Hi",
                "sections": [{"title": "A", "body": "Short text."}],
            }
        },
    )
    assert "scorecard" in qa.__dict__ or qa.scorecard is not None


def test_orchestrator_roster():
    assert len(AGENT_ROSTER) >= 10
    orch = AloraOrchestrator()
    assert any(s.agent_id == "stem_verification" for s in orch.trace)


def test_adaptations_enabled():
    """Section B profiles stay registered; only the decided nine generate."""
    from adaptation_specs import ADAPTATION_SPECS, OUTPUT_KEYS

    registered = {s["id"] for s in ADAPTATION_SPECS}
    for key in ("exam_revision", "adhd", "dyscalculia", "gifted", "tutor"):
        assert key in registered
        assert key not in OUTPUT_KEYS
    assert set(OUTPUT_KEYS) == {
        "vocabulary",
        "standard",
        "ld",
        "ell",
        "visual",
        "auditory",
        "teacher",
        "parent",
        "worksheet",
    }
