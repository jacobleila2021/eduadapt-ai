"""Publisher remediation smoke — teachability guards without new engines."""

from __future__ import annotations

from eats.checks import check_diagram, check_writing, evaluate_adaptation
from engines.lesson_composition_engine import (
    ALORA_PUBLISHER_REMEDIATION_SMOKE_OK,
    compose_lesson_package,
)
from engines.lesson_composition_engine.adaptive_writing import compose_adaptive_version
from engines.lesson_composition_engine.diagrams import build_subject_flowchart
from engines.lesson_composition_engine.publisher_remediation import (
    has_teacher_objective_leak,
    is_generic_subject_flowchart,
    remediate_adaptation,
    teachability_penalties,
    template_hits,
)
from engines.lesson_composition_engine.vocab_quality import normalize_vocab_items


def _uli() -> dict:
    return {
        "universal_profile": {
            "topic": "Force and Pressure",
            "subject": "physics",
            "concepts": ["Force", "Pressure", "Area"],
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
            "learning_objectives": [
                "Students will explain how force and pressure are related."
            ],
        }
    }


def _sif() -> dict:
    return {
        "subject_key": "physics",
        "analysis": {
            "assessment_hints": [
                {"prompt": "Define force."},
                {"prompt": "Explain pressure."},
                {"prompt": "Relate area and pressure."},
            ],
            "misconceptions": [
                {
                    "label": "Force and pressure are the same",
                    "correction": "Pressure depends on area.",
                }
            ],
        },
    }


def test_smoke_constant():
    assert ALORA_PUBLISHER_REMEDIATION_SMOKE_OK is True


def test_generic_subject_flowchart_detected():
    svg = build_subject_flowchart("physics", "Force and Pressure")
    assert is_generic_subject_flowchart(svg) is True


def test_weak_template_lesson_penalised():
    weak = {
        "topic": "Force and Pressure",
        "big_idea": (
            "Force and Pressure is worth mastering because it helps you explain "
            "Force, Pressure with accuracy and confidence."
        ),
        "sections": [
            {
                "title": "Core Idea: Force",
                "role": "concept",
                "body": "Force is a core idea in this lesson. Students will identify force.",
            },
            {
                "title": "Worked Example — Force",
                "role": "worked_example",
                "body": "Worked example: identify where force appears in the lesson evidence.",
            },
        ],
        "flowchart_svg": build_subject_flowchart("physics", "Force and Pressure"),
    }
    penalty, issues = teachability_penalties(weak)
    assert penalty >= 20
    assert issues
    diagram = check_diagram(weak)
    assert diagram.score < 85
    writing = check_writing(weak, adaptation_id="standard")
    assert writing.score < 90 or writing.issues


def test_remediate_strips_objectives_and_templates():
    polluted = {
        "topic": "The Water Cycle",
        "big_idea": "The Water Cycle is worth mastering because it helps you explain water.",
        "sections": [
            {
                "title": "Core Idea: Evaporation",
                "body": "Evaporation is a core idea in this lesson. Students will identify evaporation.",
            }
        ],
        "word_wall": [
            {
                "term": "Evaporation",
                "definition": "Students will identify evaporation, condensation, precipitation, and collection.",
            }
        ],
    }
    fixed = remediate_adaptation(
        polluted,
        claims=["Evaporation is when liquid water turns into water vapour and rises into the air."],
    )
    blob = " ".join(
        [
            str(fixed.get("big_idea") or ""),
            str((fixed.get("sections") or [{}])[0].get("body") or ""),
        ]
    )
    assert "worth mastering" not in blob.lower()
    assert "is a core idea in this lesson" not in blob.lower()
    assert not has_teacher_objective_leak(
        str((fixed.get("word_wall") or [{}])[0].get("definition") or "")
    )


def test_composed_force_pressure_avoids_legacy_templates():
    pkg = compose_lesson_package(_uli(), sif=_sif(), topic_hint="Force and Pressure")
    standard = (pkg.get("adaptations") or {}).get("standard") or {}
    blob = "\n".join(
        [
            str(standard.get("big_idea") or ""),
            *[
                str(s.get("body") or "")
                for s in (standard.get("sections") or [])
                if isinstance(s, dict)
            ],
        ]
    ).lower()
    assert "worth mastering because it helps you explain" not in blob
    assert "is a core idea in this lesson" not in blob
    assert "we begin with" not in blob or "feels clear and organised" not in blob
    assert "force is a push or a pull" in blob
    # Domain concept flowchart preferred over pedagogy stages
    svg = str(standard.get("flowchart_svg") or "")
    assert "Force" in svg or "Pressure" in svg
    assert not is_generic_subject_flowchart(svg)


def test_teacher_adaptation_not_note_spam():
    pkg = compose_lesson_package(_uli(), sif=_sif(), topic_hint="Force and Pressure")
    standard = (pkg.get("adaptations") or {}).get("standard") or {}
    teacher = compose_adaptive_version(standard, "teacher")
    bodies = "\n".join(str(s.get("body") or "") for s in (teacher.get("sections") or []) if isinstance(s, dict))
    assert bodies.lower().count("teacher note:") <= 1
    assert any(
        str(s.get("title") or "") == "Teacher Guidance"
        for s in (teacher.get("sections") or [])
        if isinstance(s, dict)
    )


def test_vocab_normalize_rejects_objectives():
    rows = normalize_vocab_items(
        [
            {
                "term": "Evaporation",
                "definition": "Students will identify evaporation, condensation, precipitation, and collection.",
            }
        ],
        topic="The Water Cycle",
        claims=["Students will identify evaporation."],
    )
    assert rows
    assert not has_teacher_objective_leak(str(rows[0].get("definition") or ""))
    assert "students will" not in str(rows[0].get("definition") or "").lower()


def test_eats_rejects_weak_template_package():
    weak = {
        "topic": "Force and Pressure",
        "big_idea": "Force and Pressure is worth mastering because it helps you explain Force.",
        "sections": [
            {"title": "Core", "role": "concept", "body": "Force is a core idea in this lesson."},
            {
                "title": "Practice",
                "role": "practice_question",
                "body": "Practice: Explain Force using evidence from the lesson.",
            },
        ],
        "flowchart_svg": build_subject_flowchart("physics", "Force and Pressure"),
    }
    result = evaluate_adaptation(weak, adaptation_id="standard", subject="physics")
    overall = float(getattr(result, "overall", None) or result.get("overall") or 0)
    # Must not look publisher-ready
    assert overall < 95


def test_publisher_remediation_smoke():
    assert ALORA_PUBLISHER_REMEDIATION_SMOKE_OK is True
    # End-to-end: compose + remediate path yields fewer template hits than legacy weak lesson
    pkg = compose_lesson_package(_uli(), sif=_sif(), topic_hint="Force and Pressure")
    standard = (pkg.get("adaptations") or {}).get("standard") or {}
    hits = template_hits(
        "\n".join(
            [
                str(standard.get("big_idea") or ""),
                *[str(s.get("body") or "") for s in (standard.get("sections") or []) if isinstance(s, dict)],
            ]
        )
    )
    assert len(hits) <= 2
    print("ALORA_PUBLISHER_REMEDIATION_SMOKE_OK")
