"""Lesson Composition Engine (LCE) 1.0 — composition, flow, vocabulary, adaptive, smoke."""

from __future__ import annotations

from engines.lesson_composition_engine import (
    LESSON_COMPOSITION_ENGINE_SMOKE_OK,
    LessonCompositionEngine,
    compose_lesson_package,
)
from engines.lesson_composition_engine.adaptive_writing import compose_adaptive_version
from engines.lesson_composition_engine.clg import build_canonical_lesson_graph
from engines.lesson_composition_engine.diagrams import (
    build_concept_map_svg,
    build_educational_flowchart_svg,
)
from engines.lesson_composition_engine.eerl import review_adaptation, review_package
from engines.lesson_composition_engine.quality_gate import evaluate_composition
from engines.lesson_composition_engine.schemas import CONCEPT_TEACHING_STEPS, QUALITY_CATEGORIES
from engines.lesson_composition_engine.vocabulary import compose_vocabulary_page, vocabulary_card_html
from engines.verified_learning_engine import reset_registry


def _sample_uli() -> dict:
    return {
        "universal_profile": {
            "topic": "Force and Pressure",
            "subject": "science",
            "concepts": ["Force", "Pressure", "Area"],
            "vocabulary": [
                {"term": "force", "definition": "A push or a pull."},
                {"term": "pressure", "definition": "Force acting on a unit area."},
                {"term": "pascal", "definition": "SI unit of pressure."},
            ],
            "misconceptions": [{"label": "Force and pressure are the same"}],
            "claim_ledger": [
                {
                    "text": "Force is a push or a pull that can change the state of motion of an object.",
                    "claim_id": "c1",
                    "source_block_ids": ["b1"],
                },
                {
                    "text": "Pressure is the force acting on a unit area of a surface.",
                    "claim_id": "c2",
                    "source_block_ids": ["b2"],
                },
                {
                    "text": "The SI unit of pressure is the pascal (Pa).",
                    "claim_id": "c3",
                    "source_block_ids": ["b3"],
                },
                {
                    "text": "For the same force, a smaller area produces greater pressure.",
                    "claim_id": "c4",
                    "source_block_ids": ["b4"],
                },
            ],
        }
    }


def _sample_sif() -> dict:
    return {
        "subject_key": "physics",
        "analysis": {
            "misconceptions": [
                {
                    "label": "Force and pressure are the same",
                    "correction": "Pressure depends on force and area.",
                }
            ],
            "assessment_hints": [
                {"prompt": "Define force using lesson evidence."},
                {"prompt": "Explain how area affects pressure."},
                {"prompt": "State the SI unit of pressure."},
                {"prompt": "Give one everyday example of pressure."},
            ],
        },
    }


def _sample_uvie() -> dict:
    return {
        "visuals": [
            {
                "visual_id": "vis_pressure",
                "caption": "Force on area diagram",
                "svg": '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="40"></svg>',
            }
        ]
    }


def test_clg_builds_from_uli_sif_uvie():
    clg = build_canonical_lesson_graph(
        _sample_uli(), sif=_sample_sif(), uvie=_sample_uvie(), topic_hint="Force and Pressure"
    )
    data = clg.to_dict()
    assert data["topic"] == "Force and Pressure"
    assert data["core_concepts"]
    assert data["vocabulary"]
    assert data["facts"]
    assert data["provenance"]["frequency_vocab_used"] is False
    assert data["visual_refs"]


def test_compose_lesson_package_adaptations():
    pkg = compose_lesson_package(
        _sample_uli(),
        sif=_sample_sif(),
        uvie=_sample_uvie(),
        topic_hint="Force and Pressure",
    )
    assert pkg["ok"] is True
    adaptations = pkg["adaptations"]
    for key in (
        "standard",
        "vocabulary",
        "worksheet",
        "ld",
        "ell",
        "visual",
        "auditory",
        "teacher",
        "parent",
        "adhd",
        "autism",
        "dyslexia",
    ):
        assert key in adaptations
    std = adaptations["standard"]
    assert std.get("big_idea")
    assert len(std.get("sections") or []) >= 8
    assert std.get("svg_diagram", "").startswith("<svg")
    assert std.get("mermaid_diagram") in ("", None)
    roles = {s.get("role") for s in std["sections"]}
    assert "summary" in roles or any("Summary" in str(s.get("title")) for s in std["sections"])
    assert "reflection" in roles or any("Reflect" in str(s.get("title")) for s in std["sections"])


def test_flow_includes_concept_teaching_steps():
    pkg = compose_lesson_package(
        _sample_uli(), sif=_sample_sif(), uvie=_sample_uvie(), topic_hint="Force and Pressure"
    )
    roles = {s.get("role") for s in (pkg["adaptations"]["standard"].get("sections") or [])}
    for step in (
        "concept",
        "simple_explanation",
        "real_life_example",
        "worked_example",
        "practice_question",
        "reflection",
    ):
        assert step in roles
    assert set(CONCEPT_TEACHING_STEPS)


def test_vocabulary_premium_cards():
    page = compose_vocabulary_page(
        [
            {"term": "pressure", "definition": "Force on unit area.", "example": "A nail tip has high pressure."},
            {"term": "force", "definition": "A push or a pull."},
            {"term": "pascal", "definition": "SI unit of pressure."},
            {"term": "area", "definition": "The measure of a surface."},
            {"term": "thrust", "definition": "Force acting perpendicular to a surface."},
        ],
        topic="Force and Pressure",
    )
    wall = page["word_wall"]
    assert len(wall) >= 5
    card = wall[0]
    # Student flashcards keep meaning/example; dictionary fields may be cleared by content fidelity.
    for field in (
        "term",
        "definition",
        "simple_explanation",
        "example_sentence",
        "color",
    ):
        assert card.get(field) not in (None, "")
    assert card.get("lce_card") is True
    html = vocabulary_card_html(card)
    assert "lce-vocab-term" in html
    assert page.get("concept_map_svg", "").startswith("<svg")
    assert page.get("mermaid_diagram") == ""


def test_visual_placement_and_diagram_quality():
    flow = build_educational_flowchart_svg("Force", ["Concept", "Example", "Practice"])
    cmap = build_concept_map_svg("Force", ["Force", "Pressure", "Area"])
    assert 'rx="' in flow and "viewBox" in flow
    assert 'rx="' in cmap and "Legend" in cmap
    pkg = compose_lesson_package(
        _sample_uli(), sif=_sample_sif(), uvie=_sample_uvie(), topic_hint="Force and Pressure"
    )
    std = pkg["adaptations"]["standard"]
    assert std["flowchart_svg"].startswith("<svg")
    visual_sections = [
        s for s in std["sections"] if s.get("role") == "visual" or s.get("visual_ids")
    ]
    assert visual_sections


def test_adaptive_versions_are_distinct():
    pkg = compose_lesson_package(
        _sample_uli(), sif=_sample_sif(), uvie=_sample_uvie(), topic_hint="Force and Pressure"
    )
    standard = pkg["adaptations"]["standard"]
    adhd = pkg["adaptations"]["adhd"]
    autism = pkg["adaptations"]["autism"]
    parent = pkg["adaptations"]["parent"]
    assert (adhd.get("lce") or {}).get("pedagogically_distinct") is True
    assert (autism.get("lce") or {}).get("pedagogically_distinct") is True
    adhd_titles = " ".join(s.get("title", "") for s in adhd.get("sections") or [])
    autism_titles = " ".join(s.get("title", "") for s in autism.get("sections") or [])
    assert "Energy Plan" in adhd_titles or "Checkpoint" in adhd_titles or "2-minute" in adhd_titles.lower() or "burst" in (adhd.get("sections") or [{}])[0].get("body", "").lower()
    assert "Lesson Map" in autism_titles or "predictable" in str(autism.get("lce")).lower()
    assert parent.get("sections")
    # Bodies should differ from standard for ADHD intro
    assert (adhd.get("sections") or [{}])[0].get("title") != (standard.get("sections") or [{}])[0].get("title") or (
        adhd.get("sections") or [{}])[0].get("body") != (standard.get("sections") or [{}])[0].get("body")
    rewritten = compose_adaptive_version(standard, "ell", vocabulary_terms=["force", "pressure"])
    assert "Key Words" in str(rewritten.get("sections")) or "Important words" in str(rewritten.get("sections"))


def test_accessibility_does_not_collapse_depth():
    pkg = compose_lesson_package(
        _sample_uli(), sif=_sample_sif(), uvie=_sample_uvie(), topic_hint="Force and Pressure"
    )
    for key in ("ld", "dyslexia", "adhd", "autism", "ell"):
        lesson = pkg["adaptations"][key]
        assert len(lesson.get("sections") or []) >= 6
        blob = " ".join(str(s.get("body") or "") for s in lesson["sections"])
        assert "force" in blob.lower() or "pressure" in blob.lower()


def test_eerl_and_quality_gate():
    pkg = compose_lesson_package(
        _sample_uli(), sif=_sample_sif(), uvie=_sample_uvie(), topic_hint="Force and Pressure"
    )
    eerl = pkg["eerl"]
    assert eerl.get("production_ready") is True
    report = review_adaptation("standard", pkg["adaptations"]["standard"], clg=pkg["clg"])
    assert report.ok
    assert not any("imagine a diagram" in str(c) for c in report.checks)
    q = evaluate_composition(
        pkg["adaptations"]["standard"],
        vocabulary=pkg["adaptations"]["vocabulary"],
        blueprint={"topic": "Force and Pressure"},
        subject="physics",
    )
    assert {s.category for s in q.scores} == set(QUALITY_CATEGORIES)
    assert q.overall >= 0.55


def test_worksheet_and_regression_no_frequency_vocab():
    pkg = compose_lesson_package(
        _sample_uli(), sif=_sample_sif(), uvie=_sample_uvie(), topic_hint="Force and Pressure"
    )
    sheet = pkg["adaptations"]["worksheet"]
    assert len(sheet.get("short_answer") or []) >= 4
    assert sheet.get("diagram_question", {}).get("svg_diagram", "").startswith("<svg")
    assert pkg["policy"]["frequency_vocab_used"] is False
    assert pkg["policy"]["mutates_curriculum"] is False
    # Package review regression
    again = review_package(pkg["adaptations"], pkg["clg"])
    assert again["production_ready"] is True


def test_vlie_engine_registration_and_process():
    reset_registry()
    eng = LessonCompositionEngine()
    health = eng.health_check()
    assert health.ok
    out = eng.process(
        {
            "uli": _sample_uli(),
            "sif": _sample_sif(),
            "uvie": _sample_uvie(),
            "topic": "Force and Pressure",
        }
    )
    assert out.ok
    assert out.payload.get("adaptations", {}).get("standard")


def test_lce_smoke():
    """LESSON_COMPOSITION_ENGINE_SMOKE_OK via standard pytest."""
    assert LESSON_COMPOSITION_ENGINE_SMOKE_OK is True
    pkg = compose_lesson_package(
        _sample_uli(), sif=_sample_sif(), uvie=_sample_uvie(), topic_hint="Force and Pressure"
    )
    assert pkg["ok"]
    assert pkg["adaptations"]["vocabulary"]["word_wall"]
    assert pkg["adaptations"]["standard"]["sections"]
    assert pkg["eerl"]["production_ready"]
    eng = LessonCompositionEngine()
    assert eng.health_check().ok
    assert eng.process(
        {"uli": _sample_uli(), "sif": _sample_sif(), "uvie": _sample_uvie(), "topic": "Force and Pressure"}
    ).ok
    print("LESSON_COMPOSITION_ENGINE_SMOKE_OK")
