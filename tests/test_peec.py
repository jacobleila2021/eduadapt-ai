"""PEEC — Product Excellence & Experience Completion tests."""

from __future__ import annotations

from peec import (
    PRODUCT_EXCELLENCE_EXPERIENCE_COMPLETION_SMOKE_OK,
    apply_peec,
    run_product_excellence_audit,
)
from peec.remediate import remediate_for_product_excellence
from peec.writing_audit import audit_lesson_writing


def test_peec_smoke_marker():
    assert PRODUCT_EXCELLENCE_EXPERIENCE_COMPLETION_SMOKE_OK is True


def test_writing_audit_flags_mechanical_tone():
    weak = {
        "standard": {
            "big_idea": "It is important to note that force is useful.",
            "sections": [
                {"title": "A", "role": "concept", "body": "In conclusion, force matters."},
                {"title": "B", "role": "concept", "body": "Furthermore, pressure matters."},
            ],
        }
    }
    report = audit_lesson_writing(weak)
    assert report["ok"] is False
    assert report["issues"]


def test_peec_remediation_scrubs_mechanical_language():
    weak = {
        "standard": {
            "topic": "Force and Pressure",
            "big_idea": "It is important to note that force is a push or a pull.",
            "sections": [
                {
                    "title": "Concept: Force",
                    "role": "concept",
                    "body": "In conclusion, force is a push or a pull.",
                },
                {
                    "title": "Example",
                    "role": "real_life_example",
                    "body": "Opening a door uses force.",
                },
                {
                    "title": "Try This",
                    "role": "practice_question",
                    "body": "Explain force.",
                },
            ],
            "flowchart_svg": (
                "<svg xmlns='http://www.w3.org/2000/svg'><rect fill='#FFF9EE'/>"
                "<text>Force</text></svg>"
            ),
            "practice": [{"question": "Explain force.", "marks": 2}],
        }
    }
    board = {
        "topic": "Force and Pressure",
        "verified_claims": ["Force is a push or a pull."],
        "concepts": [{"name": "Force"}],
        "examples": ["Opening a door uses force."],
    }
    fixed = remediate_for_product_excellence(weak, board=board)
    blob = str(fixed["standard"].get("big_idea") or "").lower()
    assert "it is important to note" not in blob
    assert fixed["standard"].get("diagram_package", {}).get("practice_question")
    assert any(
        str(s.get("role") or "") == "summary" for s in fixed["standard"].get("sections") or []
    )


def test_apply_peec_on_composed_package():
    from engines.lesson_composition_engine import compose_lesson_package
    from uevb.corpus import build_sample_sif, build_sample_uli, build_sample_uvie

    pkg = compose_lesson_package(
        build_sample_uli(
            subject="physics",
            topic="Force and Pressure",
            concept="Pressure",
            curriculum="cbse",
        ),
        sif=build_sample_sif(subject="physics", topic="Force and Pressure", concept="Pressure"),
        uvie=build_sample_uvie(topic="Force and Pressure", concept="Pressure"),
        topic_hint="Force and Pressure",
    )
    assert "peec" in pkg or pkg.get("policy", {}).get("peec_product_excellence")
    peec = pkg.get("peec") or {}
    # Compose already ran PEEC inside revise; ensure structure
    assert peec.get("smoke_ok") is True or peec.get("version") or pkg.get("ok") is True
    audit = run_product_excellence_audit(
        pkg.get("adaptations") or {},
        board=pkg.get("intelligence_board") or {},
        pmes_report=pkg.get("publisher_review_report") or {},
    )
    assert "remediation_plan" in audit
    assert "audits" in audit
    print("PRODUCT_EXCELLENCE_EXPERIENCE_COMPLETION_SMOKE_OK")
