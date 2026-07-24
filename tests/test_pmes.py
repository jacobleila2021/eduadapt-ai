"""Phase Omega 2.0 — Publisher Master Editorial System (PMES)."""

from __future__ import annotations

from engines.lesson_composition_engine import (
    PHASE_OMEGA_2_PMES_SMOKE_OK,
    STYLE_GUIDE,
    compose_lesson_package,
    critique_adaptation,
    run_pmes,
    style_guide_css,
)
from engines.lesson_composition_engine.master_teacher import craft_teaching_paragraph
from engines.lesson_composition_engine.vocabulary import vocabulary_card_html as _card_html


def _uli():
    return {
        "universal_profile": {
            "topic": "Force and Pressure",
            "subject": "physics",
            "concepts": [
                {"name": "Force", "explanation": "Force is a push or a pull."},
                {"name": "Pressure", "explanation": "Pressure is force on unit area."},
                {"name": "Area", "explanation": "Area is the measure of a surface."},
            ],
            "claim_ledger": [
                {"text": "Force is a push or a pull."},
                {"text": "Pressure equals force divided by area."},
                {"text": "A sharper tip has higher pressure for the same force."},
            ],
            "vocabulary": [
                {"term": "Force", "definition": "A push or a pull."},
                {"term": "Pressure", "definition": "Force on unit area."},
                {"term": "Pascal", "definition": "SI unit of pressure."},
                {"term": "Area", "definition": "Measure of a surface."},
            ],
            "learning_objectives": ["Explain force and pressure with examples."],
            "examples": [{"text": "A nail tip has high pressure."}],
        }
    }


def _sif():
    return {
        "subject_key": "physics",
        "analysis": {
            "misconceptions": [
                {
                    "label": "Pressure is the same as force",
                    "correction": "Pressure depends on both force and area.",
                }
            ],
            "assessment_hints": [{"prompt": "Why does a sharp knife cut more easily?"}],
        },
    }


def test_pmes_smoke_marker():
    assert PHASE_OMEGA_2_PMES_SMOKE_OK is True
    assert STYLE_GUIDE["version"] == "2.0.0"
    css = style_guide_css()
    assert "#FFF9EE" in css
    assert "pmes-flashcard" in css


def test_master_teacher_paragraph_has_teaching_arc():
    text = craft_teaching_paragraph(
        claim="Force is a push or a pull.",
        topic="Force and Pressure",
        concept="Force",
        example="Opening a door uses a push.",
        profile="standard",
    )
    low = text.lower()
    assert "force" in low
    assert "notice how" not in low
    assert "core idea" not in low
    assert len(text.split()) >= 20


def test_vocabulary_flashcard_html_is_premium():
    html = _card_html(
        {
            "term": "Pressure",
            "pronunciation": "PRESH-er",
            "part_of_speech": "noun",
            "definition": "Force on unit area.",
            "simple_explanation": "How concentrated a force is on a surface.",
            "example_sentence": "A nail tip has high pressure.",
            "memory_tip": "Picture the tip of a pin.",
            "picture": "A pin point pressing into wood.",
            "color": "#FFFDF6",
            "emoji": "📌",
        }
    )
    assert "pmes-flashcard" in html
    assert "PRESSURE" in html
    assert "Remember" in html
    assert "Real-life example" in html or "In real life" in html


def test_pmes_rewrites_until_diagram_package_exists():
    weak = {
        "topic": "Force and Pressure",
        "big_idea": "Force is a push or a pull.",
        "sections": [
            {
                "title": "Concept: Force",
                "role": "concept",
                "body": "Force is a push or a pull.",
            },
            {
                "title": "Example — Force",
                "role": "real_life_example",
                "body": "Opening a door uses force.",
            },
            {
                "title": "Try This — Force",
                "role": "practice_question",
                "body": "Explain force in your own words.",
            },
            {
                "title": "Lesson Summary",
                "role": "summary",
                "body": "Force and pressure work together.",
            },
        ],
        "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'><text>Force</text><text>Pressure</text></svg>",
        "practice": [{"question": "Explain pressure.", "marks": 2}],
    }
    board = {
        "topic": "Force and Pressure",
        "subject": "physics",
        "verified_claims": ["Force is a push or a pull.", "Pressure equals force divided by area."],
        "concepts": [{"name": "Force"}, {"name": "Pressure"}],
        "examples": ["A nail tip has high pressure."],
    }
    first = critique_adaptation(weak, adaptation_id="standard", board=board)
    assert first["approved"] is False
    assert any("comment" in c for c in first["comments"])
    result = run_pmes({"standard": weak}, board=board, max_passes=4)
    std = result["adaptations"]["standard"]
    assert std.get("diagram_package", {}).get("caption")
    assert std.get("diagram_package", {}).get("practice_question")
    assert result.get("publisher_review_report", {}).get("schema")


def test_compose_includes_pmes_report():
    pkg = compose_lesson_package(_uli(), sif=_sif(), topic_hint="Force and Pressure")
    assert pkg.get("policy", {}).get("pmes_highest_authority") is True
    assert "publisher_review_report" in pkg
    std = (pkg.get("adaptations") or {}).get("standard") or {}
    assert std.get("diagram_package") or std.get("lce", {}).get("pmes")
    vocab = (pkg.get("adaptations") or {}).get("vocabulary") or {}
    wall = vocab.get("word_wall") or []
    if wall:
        html = _card_html(wall[0])
        assert "pmes-flashcard" in html or "lce-vocab-term" in html
    print("PHASE_OMEGA_2_PMES_SMOKE_OK")
