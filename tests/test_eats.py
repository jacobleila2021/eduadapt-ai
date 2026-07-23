"""Educational Acceptance Testing System (EATS) — unit, integration, regression, smoke."""

from __future__ import annotations

from publication_gate import publication_allowed, publication_block_reason

from eats import (
    EDUCATIONAL_ACCEPTANCE_TESTING_SYSTEM_SMOKE_OK,
    PUBLISHER_READY,
    accept_lesson,
    attach_eats_to_adaptations,
    build_dashboard_state,
    evaluate_package,
    pack_health,
)
from eats.checks import check_writing, evaluate_adaptation
from eats.constants import band_for_score, verdict_for_score
from eats.golden_library import list_eats_goldens
from eats.screenshots import adaptation_html, capture_adaptation_snapshots


def _uli():
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
        }
    }


def _sif():
    return {
        "subject_key": "physics",
        "analysis": {
            "assessment_hints": [
                {"prompt": "Define force."},
                {"prompt": "Explain pressure."},
                {"prompt": "Relate area and pressure."},
                {"prompt": "Give one everyday example."},
            ],
            "misconceptions": [
                {
                    "label": "Force and pressure are the same",
                    "correction": "Pressure depends on area.",
                }
            ],
        },
    }


def _compose_adaptations():
    from engines.lesson_composition_engine import compose_lesson_package

    pkg = compose_lesson_package(_uli(), sif=_sif(), topic_hint="Force and Pressure")
    return pkg.get("adaptations") or {}


def test_smoke_constant():
    assert EDUCATIONAL_ACCEPTANCE_TESTING_SYSTEM_SMOKE_OK is True
    print("EDUCATIONAL_ACCEPTANCE_TESTING_SYSTEM_SMOKE_OK")


def test_pack_health():
    health = pack_health()
    assert health["ok"] is True
    assert health["threshold"] == PUBLISHER_READY


def test_bands_and_verdicts():
    assert band_for_score(96) == "publisher_ready"
    assert band_for_score(92) == "excellent"
    assert band_for_score(86) == "good"
    assert band_for_score(82) == "needs_improvement"
    assert band_for_score(70) == "reject"
    assert verdict_for_score(96) == "pass"
    assert verdict_for_score(90) == "revise"
    assert verdict_for_score(70) == "reject"


def test_writing_rejects_robotic_ai():
    dim = check_writing(
        {
            "big_idea": "In this lesson we will explore force carefully.",
            "sections": [
                {
                    "title": "Idea",
                    "role": "concept",
                    "body": "It is important to note that force is a push. Let's explore pressure next.",
                }
            ],
        },
        adaptation_id="standard",
    )
    assert dim.score < 85
    assert any("Robotic" in i or "AI" in i for i in dim.issues)


def test_rejects_plain_vocabulary_lists():
    result = evaluate_adaptation(
        {"words": [{"term": "Force"}, {"term": "Pressure"}]},
        adaptation_id="vocabulary",
    )
    assert result.overall < 80 or result.verdict == "reject"
    assert result.dimensions["vocabulary"].score < 70


def test_adaptation_personalities_differ():
    ads = _compose_adaptations()
    package = evaluate_package(ads, subject="physics")
    assert "adhd" in package.by_adaptation
    assert "autism" in package.by_adaptation
    assert "ell" in package.by_adaptation
    assert package.by_adaptation["adhd"].dimensions["adaptation"].score >= 85
    assert package.by_adaptation["autism"].dimensions["adaptation"].score >= 85


def test_lce_lesson_passes_educational_acceptance():
    ads = _compose_adaptations()
    result = accept_lesson(
        ads,
        subject="physics",
        topic="Force and Pressure",
        auto_revise=False,
        capture_screenshots=True,
        try_png=False,
    )
    assert result["ok"] is True
    assert result["verdict"] == "pass"
    assert result["eats_meta"]["overall"] >= PUBLISHER_READY
    assert result["adaptations"]["_meta"]["eats"]["publication_ready"] is True
    assert result["report_paths"]["json"]
    assert result["screenshots"]["dir"]


def test_publication_gate_blocks_failed_eats():
    adaptations = {
        "_meta": {
            "eats": {
                "publication_ready": False,
                "reject_rendering": True,
                "overall": 72.0,
                "verdict": "reject",
            }
        }
    }
    reason = publication_block_reason(adaptations)
    assert "Educational Acceptance" in reason
    assert not publication_allowed(adaptations)


def test_attach_eats_hook():
    ads = _compose_adaptations()
    merged = attach_eats_to_adaptations(
        ads,
        subject="physics",
        topic="Force and Pressure",
        auto_revise=False,
        capture_screenshots=False,
    )
    assert "eats" in (merged.get("_meta") or {})
    assert merged["_meta"]["eats"]["overall"] >= PUBLISHER_READY


def test_screenshot_html_and_mosaic():
    html = adaptation_html(
        "standard",
        {
            "title": "Force",
            "big_idea": "Force is a push or a pull.",
            "sections": [{"title": "Idea", "role": "concept", "body": "Push or pull."}],
            "flowchart_svg": (
                '<svg xmlns="http://www.w3.org/2000/svg" role="img" '
                'aria-label="x"><text>Force</text></svg>'
            ),
        },
    )
    assert "Force" in html
    assert "big-idea" in html
    snap = capture_adaptation_snapshots(
        {"standard": {"title": "Force", "big_idea": "Push.", "sections": []}},
        run_id="eats_test_snap",
        try_png=False,
    )
    assert snap["dir"]
    assert snap["manifest"]["mosaic"]


def test_dashboard_builds():
    state = build_dashboard_state()
    assert "pass_rate" in state
    assert "publisher_quality_index" in state
    assert "adaptation_performance" in state


def test_golden_library_lists_exemplars():
    rows = list_eats_goldens()
    assert isinstance(rows, list)


def test_weak_lesson_rejected():
    weak = {
        "standard": {
            "big_idea": "In this lesson we will explore stuff.",
            "sections": [
                {"title": "A", "body": "Delve into the topic. Certainly! Great question."},
            ],
        },
        "vocabulary": {"words": [{"term": "x"}]},
        "worksheet": {},
    }
    package = evaluate_package(weak, subject="general")
    assert package.overall < 80 or package.verdict in ("reject", "revise")
    assert package.publication_ready is False
