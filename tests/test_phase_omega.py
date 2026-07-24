"""Phase Omega — Intelligence Board, editorial board, distinct adaptations."""

from __future__ import annotations

from engines.lesson_composition_engine import (
    PHASE_OMEGA_PREMIUM_EDUCATIONAL_EXPERIENCE_SMOKE_OK,
    build_lesson_intelligence_board,
    compose_lesson_package,
    review_package_editorial,
)
from engines.lesson_composition_engine.board_adaptations import compose_adaptation_from_board


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
                {"term": "Force"},
                {"term": "Pressure"},
                {"term": "Pascal"},
            ],
            "learning_objectives": ["Explain force and pressure with examples."],
            "examples": [{"text": "A nail tip has high pressure."}],
            "prerequisites": [{"text": "Know what a push and a pull feel like."}],
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
            "prerequisites": [{"text": "Basic measurement of area"}],
        },
    }


def test_phase_omega_smoke_marker():
    assert PHASE_OMEGA_PREMIUM_EDUCATIONAL_EXPERIENCE_SMOKE_OK is True


def test_intelligence_board_before_authoring():
    board = build_lesson_intelligence_board(
        {
            "topic": "Force and Pressure",
            "subject_key": "physics",
            "facts": [{"text": "Force is a push or a pull."}],
            "core_concepts": [{"name": "Force"}, {"name": "Pressure"}],
            "misconceptions": [{"label": "Pressure equals force", "correction": "Include area."}],
            "learning_goals": [{"text": "Explain pressure using force and area."}],
            "vocabulary": [{"term": "Pascal"}],
            "visual_refs": [{"caption": "Force and pressure organiser", "kind": "flowchart"}],
        },
        uli=_uli(),
        sif=_sif(),
    )
    assert board["schema"] == "alora.lesson_intelligence_board.v1"
    assert board["ready_to_author"] is True
    assert board["verified_claims"]
    assert board["concepts"]
    assert "standard" in board["learner_profiles"]


def test_adaptations_are_pedagogically_distinct():
    board = build_lesson_intelligence_board(
        {
            "topic": "Force and Pressure",
            "subject_key": "physics",
            "facts": [{"text": "Force is a push or a pull."}],
            "claim_texts": ["Pressure equals force divided by area."],
            "core_concepts": [
                {"name": "Force", "explanation": "Force is a push or a pull."},
                {"name": "Pressure", "explanation": "Pressure is force on unit area."},
            ],
            "misconceptions": [
                {"label": "Pressure is the same as force", "correction": "Pressure uses area."}
            ],
            "learning_goals": [{"text": "Explain force and pressure."}],
            "examples": [{"text": "A nail tip has high pressure."}],
            "visual_refs": [{"caption": "Force–pressure map"}],
        },
        uli=_uli(),
        sif=_sif(),
    )
    svg = "<svg xmlns='http://www.w3.org/2000/svg'><text>Force</text><text>Pressure</text></svg>"
    adhd = compose_adaptation_from_board(board, "adhd", flowchart_svg=svg, concept_map_svg=svg)
    autism = compose_adaptation_from_board(board, "autism", flowchart_svg=svg, concept_map_svg=svg)
    ell = compose_adaptation_from_board(board, "ell", flowchart_svg=svg, concept_map_svg=svg)
    titles_adhd = [str(s.get("title") or "") for s in adhd["sections"]]
    titles_autism = [str(s.get("title") or "") for s in autism["sections"]]
    titles_ell = [str(s.get("title") or "") for s in ell["sections"]]
    assert any("Mission" in t or "Chunk" in t or "Minute" in t for t in titles_adhd)
    assert any("Routine" in t or "What We Will" in t or "Finished" in t for t in titles_autism)
    assert any("Key Words" in t for t in titles_ell)
    assert titles_adhd != titles_autism
    assert adhd["lce"]["pedagogically_distinct"] is True


def test_compose_package_phase_omega_end_to_end():
    pkg = compose_lesson_package(_uli(), sif=_sif(), topic_hint="Force and Pressure")
    assert pkg.get("intelligence_board")
    assert pkg.get("policy", {}).get("phase_omega") is True
    assert pkg.get("pqle", {}).get("smoke_ok") is True
    std = (pkg.get("adaptations") or {}).get("standard") or {}
    roles = {s.get("role") for s in (std.get("sections") or []) if isinstance(s, dict)}
    assert "concept" in roles
    assert "visual" in roles
    assert "practice_question" in roles
    assert std.get("lce", {}).get("from_intelligence_board") is True
    editorial = pkg.get("editorial") or review_package_editorial(
        pkg.get("adaptations") or {}, board=pkg.get("intelligence_board") or {}
    )
    assert "editors" in editorial
    print("PHASE_OMEGA_PREMIUM_EDUCATIONAL_EXPERIENCE_SMOKE_OK")
