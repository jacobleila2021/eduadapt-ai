"""UEVB — Universal Educational Validation & Benchmarking tests."""

from __future__ import annotations

from uevb import (
    UNIVERSAL_EDUCATIONAL_VALIDATION_BENCHMARKING_SMOKE_OK,
    corpus_size,
    gate_package_for_production,
    pack_health,
    validate_composed_package,
)
from uevb.corpus import build_sample_uli, iter_corpus_specs
from uevb.differentiation import measure_adaptation_differentiation
from uevb.engine_contribution import measure_engine_contributions


def test_uevb_smoke_marker():
    assert UNIVERSAL_EDUCATIONAL_VALIDATION_BENCHMARKING_SMOKE_OK is True
    health = pack_health()
    assert health["ok"] is True
    size = corpus_size()
    assert size["lesson_specs"] >= 100  # 12 subjects × 10 curricula × ≥1 topic
    assert size["adaptation_pages"] > size["lesson_specs"]


def test_corpus_specs_cover_matrix():
    specs = iter_corpus_specs(max_topics_per_subject=1)
    subjects = {s["subject"] for s in specs}
    curricula = {s["curriculum"] for s in specs}
    assert "physics" in subjects and "biology" in subjects
    assert "cbse" in curricula and "cambridge" in curricula
    uli = build_sample_uli(subject="physics", topic="Force and Pressure", concept="Pressure")
    assert uli["universal_profile"]["topic"] == "Force and Pressure"


def test_differentiation_rejects_clones():
    standard = {
        "big_idea": "Force is a push or a pull.",
        "sections": [
            {"title": "Concept: Force", "role": "concept", "body": "Force is a push or a pull."},
            {"title": "Example", "role": "real_life_example", "body": "Opening a door."},
            {"title": "Practice", "role": "practice_question", "body": "Explain force."},
        ],
    }
    clone = {
        "big_idea": "Force is a push or a pull.",
        "sections": [
            {"title": "Concept: Force", "role": "concept", "body": "Force is a push or a pull."},
            {"title": "Example", "role": "real_life_example", "body": "Opening a door."},
            {"title": "Practice", "role": "practice_question", "body": "Explain force."},
        ],
    }
    distinct = {
        "big_idea": "Mission: learn force in short bursts.",
        "sections": [
            {"title": "Mission Goal", "role": "hook", "body": "Work in two-minute chunks."},
            {"title": "2-Minute Chunk 1: Force", "role": "concept", "body": "- Force is a push or a pull"},
            {"title": "Movement Break", "role": "reflection", "body": "Stand and stretch."},
            {"title": "Done Checklist", "role": "summary", "body": "Tick each idea."},
        ],
    }
    bad = measure_adaptation_differentiation({"standard": standard, "adhd": clone})
    good = measure_adaptation_differentiation({"standard": standard, "adhd": distinct})
    assert bad["adaptation_differentiation_score"] < good["adaptation_differentiation_score"]
    assert "adhd" in bad["cosmetic_failures"] or not bad["ok"]


def test_engine_contribution_flags_empty_package():
    report = measure_engine_contributions({}, board={}, subject="physics")
    assert report["integration_failures"]
    assert "LCE" in report["integration_failures"]


def test_validate_and_gate_composed_package():
    from engines.lesson_composition_engine import compose_lesson_package

    uli = build_sample_uli(
        subject="physics",
        topic="Force and Pressure",
        concept="Pressure",
        curriculum="cbse",
    )
    pkg = compose_lesson_package(
        uli,
        sif={
            "subject_key": "physics",
            "analysis": {
                "misconceptions": [
                    {"label": "Pressure equals force", "correction": "Include area."}
                ],
                "assessment_hints": [{"prompt": "Explain pressure."}],
            },
        },
        uvie={
            "preferred_visuals": [
                {"caption": "Force–pressure map", "kind": "flowchart", "visual_id": "fp1"}
            ]
        },
        topic_hint="Force and Pressure",
    )
    validation = validate_composed_package(pkg)
    assert "engine_contribution_report" in validation
    assert "adaptation_differentiation_report" in validation
    assert "publisher_benchmark_report" in validation
    assert "visual_design_audit" in validation
    gated = gate_package_for_production(pkg)
    assert "release_gate" in gated
    assert pkg.get("policy", {}).get("uevb_final_authority") is True or "uevb" in pkg
    print("UNIVERSAL_EDUCATIONAL_VALIDATION_BENCHMARKING_SMOKE_OK")
