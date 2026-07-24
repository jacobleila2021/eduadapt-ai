"""RCPR — Release Candidate & Production Readiness tests."""

from __future__ import annotations

from release import (
    RC_TAG,
    RELEASE_CANDIDATE_PRODUCTION_READINESS_SMOKE_OK,
)
from release.defects import classify_package_defects, auto_resolve_critical_high
from release.report import build_rc1_report


def test_rcpr_smoke_marker():
    assert RELEASE_CANDIDATE_PRODUCTION_READINESS_SMOKE_OK is True
    assert RC_TAG == "ALORA-AI-RC1"


def test_classify_detects_scaffold_and_missing_adaptations():
    package = {
        "ok": False,
        "adaptations": {
            "standard": {
                "sections": [
                    {"title": "A", "body": "Notice how force works in this example carefully."},
                    {"title": "B", "body": "Force is a push or a pull on an object."},
                ],
                "flowchart_svg": "<svg></svg>",
            }
        },
    }
    defects = classify_package_defects(package, corpus_id="test.physics")
    codes = {d["code"] for d in defects}
    assert "publication_not_ready" in codes
    assert "missing_adaptation" in codes
    assert "scaffold_leak" in codes


def test_auto_resolve_marks_medium_documented():
    package = {
        "ok": True,
        "corpus_id": "test.thin",
        "intelligence_board": {"topic": "Force", "subject": "physics"},
        "adaptations": {
            "standard": {
                "sections": [
                    {"title": "Concept", "body": "Force is a push or a pull."},
                    {"title": "Example", "body": "Opening a door uses force."},
                    {"title": "Practice", "body": "Explain force in one sentence."},
                ],
                "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                "diagram_package": {"title": "Force"},
            },
            "vocabulary": {"word_wall": [{"term": "a"}, {"term": "b"}, {"term": "c"}, {"term": "d"}]},
            "adhd": {
                "sections": [
                    {"title": "Mission", "body": "Learn force in short bursts today."},
                    {"title": "Chunk", "body": "Force is a push or a pull."},
                    {"title": "Break", "body": "Stand and stretch for thirty seconds."},
                ],
                "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                "diagram_package": {"practice_question": "What is force?"},
            },
            "autism": {
                "sections": [
                    {"title": "Predictable", "body": "Today we study force step by step."},
                    {"title": "Definition", "body": "Force is a push or a pull."},
                    {"title": "Check", "body": "Write the definition once."},
                ],
                "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                "diagram_package": {"practice_question": "Define force."},
            },
            "ell": {
                "sections": [
                    {"title": "Words", "body": "Force means a push or a pull."},
                    {"title": "Example", "body": "You use force to open a door."},
                    {"title": "Say it", "body": "Say: force is a push or a pull."},
                ],
                "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                "diagram_package": {"practice_question": "What does force mean?"},
            },
            "visual": {
                "sections": [
                    {"title": "See it", "body": "Look at the arrows for push and pull."},
                    {"title": "Label", "body": "Label each arrow as push or pull."},
                    {"title": "Recall", "body": "Force is a push or a pull."},
                ],
                "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                "diagram_package": {"practice_question": "Label the force arrows."},
                "style_guide": {"background": "#FFFFFF"},
            },
            "auditory": {
                "sections": [
                    {"title": "Listen", "body": "Say force aloud three times."},
                    {"title": "Meaning", "body": "Force is a push or a pull."},
                    {"title": "Retell", "body": "Tell a partner what force means."},
                ],
                "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                "diagram_package": {"practice_question": "Retell the meaning of force."},
            },
            "teacher": {
                "sections": [
                    {"title": "Aim", "body": "Learners explain force clearly."},
                    {"title": "Teach", "body": "Model push and pull with a door."},
                    {"title": "Assess", "body": "Ask for one example of force."},
                ],
                "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                "diagram_package": {"practice_question": "Exit ticket on force."},
            },
            "parent": {
                "sections": [
                    {"title": "Home", "body": "Ask your child what force means."},
                    {"title": "Try", "body": "Open a door together and name the force."},
                    {"title": "Praise", "body": "Praise a clear definition."},
                ],
            },
            "worksheet": {
                "diagram_question": {"svg_diagram": "<svg xmlns='http://www.w3.org/2000/svg'></svg>"},
            },
            "ld": {
                "sections": [
                    {"title": "Step 1", "body": "Force is a push or a pull."},
                    {"title": "Step 2", "body": "Try opening a door slowly."},
                    {"title": "Step 3", "body": "Write one force example."},
                ],
                "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                "diagram_package": {"practice_question": "Give one force example."},
            },
            "dyslexia": {
                "sections": [
                    {"title": "Short line", "body": "Force is a push or a pull."},
                    {"title": "Example", "body": "Open a door."},
                    {"title": "Check", "body": "Say the meaning once."},
                ],
                "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'></svg>",
                "diagram_package": {"practice_question": "Say what force means."},
            },
        },
        "pmes": {"approved": True},
        "uevb": {"ok": True},
        "peec": {"ok": True},
    }
    defects = classify_package_defects(package, corpus_id="test.thin")
    assert any(d["code"] == "diagram_not_teaching" for d in defects)
    _pkg, _resolved, remaining = auto_resolve_critical_high(dict(package), defects)
    assert any(d.get("status") == "documented" for d in remaining if d["severity"] == "medium")


def test_rc1_report_shape():
    campaign = {
        "rc1_ready": True,
        "packages_ok": 100,
        "packages_targeted": 100,
        "subjects": ["physics"],
        "curricula": ["cbse"],
        "performance": {"avg_package_seconds": 1.0},
        "defects": {
            "critical_open_count": 0,
            "high_open_count": 0,
            "critical_open": [],
            "high_open": [],
            "medium_documented": [],
            "low_documented": [],
            "resolved": [],
        },
    }
    report = build_rc1_report(campaign)
    assert report["tag"] == "ALORA-AI-RC1"
    assert report["executive_summary"]["rc1_ready"] is True
    assert report["stop_condition"]["development_frozen"] is True


def test_rc1_smoke_campaign():
    from release.campaign import run_rc1_campaign

    result = run_rc1_campaign(
        target_packages=2,
        subjects=("physics", "biology"),
        curricula=("cbse",),
        max_topics_per_subject=1,
        compose=True,
        auto_fix=True,
    )
    assert result["packages_targeted"] == 2
    assert "performance" in result
    assert result["architecture_frozen"] is True
    # Critical/High may still surface in thin corpus fixtures; campaign must record them honestly.
    assert "critical_open_count" in result["defects"]
    assert "high_open_count" in result["defects"]
