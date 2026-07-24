"""Regression: exam-ready classroom adaptations + closed water-cycle visuals."""

from __future__ import annotations

from ai_generator import (
    CLASSROOM_LESSON_KEYS,
    _lesson_prompt,
    _source_fallback_lesson,
    _valid_lesson,
)
from knowledge.prompts import (
    BULLET_SECTION_RULES,
    DIFFERENTIATION_RULES,
)
from knowledge.service import inject_exam_practice_into_lessons
from adaptation_specs import ADAPTATION_SPECS


def test_ld_rules_no_longer_collapse_to_grade_3_4():
    # Must not mandate Grade 3–4 as the target reading level (prohibition text is OK).
    assert "simplified vocabulary (Grade 3" not in DIFFERENTIATION_RULES
    assert "Grade 3-4)" not in BULLET_SECTION_RULES
    assert "grade-matched" in DIFFERENTIATION_RULES.lower()
    ld = next(s for s in ADAPTATION_SPECS if s["id"] == "ld")
    assert "simplified language (Grade 3" not in ld["hint"]
    assert "exam" in ld["hint"].lower()
    assert "source grade" in ld["hint"].lower() or "NOT Grade 3" in ld["hint"]


def test_classroom_policy_pack_wired_into_lesson_prompt():
    prompt = _lesson_prompt("ld", "Dyslexia Smart", "hint")
    assert "CLASSROOM TEACHING FLOW" in prompt
    assert "BOARD / EXAM READINESS" in prompt
    assert "Exam Practice" in prompt
    assert "standard" in CLASSROOM_LESSON_KEYS


def test_valid_lesson_rejects_thin_classroom_condensation():
    thin = {
        "big_idea": "Water moves.",
        "sections": [
            {"title": f"Part {i}", "body": "Short stub."} for i in range(6)
        ],
    }
    assert _valid_lesson(thin)  # legacy non-classroom gate still passes
    assert not _valid_lesson(thin, classroom=True)

    rich_body = (
        "Teach this classroom segment carefully with clear exam terminology. "
        + ("Students explain evaporation using accurate board terminology and evidence. " * 10)
    )
    rich = {
        "big_idea": "Students explain the closed water cycle and answer board questions.",
        "sections": [
            {"title": "Learning Goal", "body": rich_body},
            {"title": "Evaporation", "body": rich_body},
            {"title": "Condensation", "body": rich_body},
            {"title": "Guided Practice", "body": rich_body},
            {"title": "Independent Practice", "body": rich_body},
            {"title": "Exam Practice", "body": rich_body + " Q1. Explain evaporation."},
            {"title": "Summary", "body": rich_body},
        ],
    }
    assert _valid_lesson(rich, classroom=True)


def test_valid_lesson_rejects_stub_bullets_in_classroom_mode():
    bullets = "\n".join(f"- word{i}" for i in range(8))
    lesson = {
        "big_idea": "Topic",
        "sections": [{"title": f"S{i}", "body": bullets} for i in range(6)],
    }
    assert not _valid_lesson(lesson, classroom=True)


def test_classroom_fallback_includes_exam_practice():
    profile = {
        "topic": "The Water Cycle",
        "title": "The Water Cycle",
        "claim_ledger": [
            {"text": "Evaporation turns liquid water into water vapour."},
            {"text": "Condensation forms clouds from cooling vapour."},
            {"text": "Precipitation returns water to Earth as rain."},
            {"text": "Collection gathers water in oceans, rivers, and lakes."},
            {"text": "Transpiration releases water vapour from plants."},
            {"text": "The sun supplies energy that drives the cycle."},
        ],
        "key_concepts": [
            {"name": "Evaporation"},
            {"name": "Condensation"},
            {"name": "Precipitation"},
        ],
    }
    lesson = _source_fallback_lesson("ld", profile, ["blk_1"])
    titles = [s["title"] for s in lesson["sections"]]
    assert any("Exam Practice" in t for t in titles)
    exam = next(s for s in lesson["sections"] if "Exam Practice" in s["title"])
    assert "Board-style practice" in exam["body"]
    assert "not an official" in exam["body"].lower()
    assert _valid_lesson(lesson, classroom=True)


def test_inject_exam_practice_source_bound_when_bank_empty():
    adaptations = {
        "standard": {
            "big_idea": "Cells",
            "sections": [{"title": "Intro", "body": "Plant cells have walls."}],
        },
        "ld": {
            "big_idea": "Cells",
            "sections": [{"title": "Intro", "body": "Plant cells have walls."}],
        },
        "vocabulary": {"topic": "Cells"},
    }
    out = inject_exam_practice_into_lessons(
        adaptations,
        {},
        universal_profile={
            "topic": "Plant Cells",
            "claim_ledger": [
                {"text": "Plant cells have a cell wall."},
                {"text": "Chloroplasts perform photosynthesis."},
            ],
        },
    )
    for key in ("standard", "ld"):
        titles = [s["title"] for s in out[key]["sections"]]
        assert any("Exam Practice" in t for t in titles)
        body = out[key]["sections"][-1]["body"]
        assert "practice-from-source" in body or "Board-style practice" in body
    assert "sections" not in (out.get("vocabulary") or {})


def test_water_cycle_svg_is_closed_loop():
    from flowchart_builder import _water_cycle_visual_svg
    from study_diagram_builder import build_study_diagram_svg

    svg = _water_cycle_visual_svg("The Water Cycle")
    assert (
        "Closed water cycle" in svg
        or "closed cycle" in svg.lower()
        or "(repeat)" in svg.lower()
    )
    for label in ("Evaporation", "Condensation", "Precipitation", "Collection", "Transpiration"):
        assert label in svg
    assert "Evaporation → Condensation → Precipitation → Collection" in svg
    assert "side loop" in svg.lower() or "Transpiration" in svg

    study = build_study_diagram_svg(
        {"topic": "The Water Cycle", "sections": [{"title": "Evaporation", "body": "Heat."}]}
    )
    assert "Evaporation" in study and "Collection" in study
    assert (
        "Evaporation → Condensation → Precipitation → Collection → Evaporation" in study
        or "Evaporation → Condensation → Precipitation → Collection" in study
    )


def test_renderer_uses_uvie_svg_and_mermaid_without_asset_paths(monkeypatch):
    import structured_renderers as sr

    calls = {"svg": [], "mermaid": []}

    class _Col:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def markdown(self, *a, **k):
            return None

    class _St:
        def markdown(self, *a, **k):
            return None

        def caption(self, *a, **k):
            return None

        def image(self, *a, **k):
            raise AssertionError("asset image should not be required")

        def columns(self, n):
            return [_Col() for _ in range(n)]

        class components:
            class v1:
                @staticmethod
                def iframe(*a, **k):
                    raise AssertionError("iframe not expected")

    monkeypatch.setattr(sr, "st", _St())
    monkeypatch.setattr(sr, "_render_svg", lambda svg, height=260: calls["svg"].append(svg))
    monkeypatch.setattr(sr, "_render_mermaid", lambda m: calls["mermaid"].append(m))

    svg_payload = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="120">'
        '<rect x="10" y="10" width="180" height="40" fill="#0284c7"/>'
        "<text x='20' y='35'>Evaporation</text></svg>"
    )
    lesson_svg = {
        "big_idea": "Cycle",
        "sections": [{"title": "A", "body": "body text for the section"}],
        "verified_visuals": [{"caption": "UVIE organiser", "svg": svg_payload}],
    }
    sr.render_lesson(lesson_svg, "standard")
    assert calls["svg"], "expected UVIE svg to render"

    calls["svg"].clear()
    lesson_m = {
        "big_idea": "Cycle",
        "sections": [{"title": "A", "body": "body text for the section"}],
        "verified_visuals": [
            {
                "caption": "UVIE mermaid",
                "mermaid": "flowchart TD\n  A[Evaporation] --> B[Condensation]",
            }
        ],
    }
    sr.render_lesson(lesson_m, "standard")
    assert calls["mermaid"], "expected UVIE mermaid to render"
