"""Learner chrome removal, full topic titles, and chemistry diagrams."""

from __future__ import annotations

from engines.lesson_composition_engine.composer import compose_worksheet_from_clg
from engines.lesson_composition_engine.content_fidelity import scrub_learner_chrome
from engines.lesson_composition_engine.vocab_quality import filter_diagram_stages
from workspace_page import _clean_title


def test_clean_title_keeps_acids_bases_and_salts():
    assert _clean_title("Acids, Bases and Salts") == "Acids, Bases and Salts"
    assert "Salts" in _clean_title("Acids, Bases and Salts — Class 8")


def test_scrub_removes_forbidden_chrome():
    page = scrub_learner_chrome(
        {
            "big_idea": "Recall how we tested sour and bitter substances.",
            "topic": "Acids, Bases and Salts",
            "sections": [
                {"title": "Step by Step", "body": "Read one line."},
                {"title": "Reflect: I Can", "body": "I can explain acids."},
                {"title": "Must-Learn Ideas", "role": "concept_primer", "body": "…"},
                {"title": "Big Idea", "body": "…"},
                {"title": "Using the Diagram", "body": "Trace labels."},
                {"title": "Acid", "body": "An acid tastes sour and turns blue litmus red."},
            ],
            "diagram_package": {
                "caption": "Acids: how the key ideas connect",
                "explanation": "how the key ideas connect",
            },
        }
    )
    titles = [s["title"] for s in page["sections"]]
    assert titles == ["Acid"]
    assert not page.get("big_idea")
    assert "diagram_package" not in page  # no SVG → package dropped


def test_chemistry_diagram_stages_seeded():
    stages = filter_diagram_stages(
        ["EVIOUS", "solution", "Acid"],
        topic="Acids, Bases and Salts",
        claims=[],
        limit=5,
    )
    low = {s.lower() for s in stages}
    assert "acid" in low
    assert "base" in low
    assert "salt" in low
    assert "evious" not in low


def test_worksheet_eight_mark_answers_use_real_definitions():
    sheet = compose_worksheet_from_clg(
        {
            "topic": "Acids, Bases and Salts",
            "subject_key": "science",
            "facts": [
                {
                    "text": (
                        "Acids, Bases and Salts 2CHAPTER Y ou have lear nt in your "
                        "pr evious classes that the sour and bitter tastes of food "
                        "are due to acids and bases."
                    )
                }
            ],
            "core_concepts": [
                {"name": "Salts", "explanation": ""},
                {"name": "Baking soda", "explanation": ""},
            ],
        }
    )
    blob = " ".join(str(q.get("model_answer") or "") for q in sheet["long_answer"]).lower()
    assert "2chapter" not in blob
    assert "one of the ideas taught" not in blob
    assert "litmus" in blob or "sour" in blob or "salt" in blob
    svg = str((sheet.get("diagram_question") or {}).get("svg_diagram") or "")
    assert svg.startswith("<svg")
    assert "Acid" in svg or "acid" in svg.lower()
