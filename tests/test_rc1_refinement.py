"""RC1 product refinement — golden library coverage."""

from __future__ import annotations

from engines.lesson_composition_engine.golden import golden_library_health, load_golden
from release import PRODUCT_REFINEMENT_RC1_SMOKE_OK, rc1_product_health


def test_rc1_product_refinement_smoke():
    assert PRODUCT_REFINEMENT_RC1_SMOKE_OK is True
    health = rc1_product_health()
    assert health["smoke_ok"] is True
    assert health["ok"] is True
    assert health["count"] >= 10


def test_golden_library_covers_major_subjects():
    health = golden_library_health()
    assert health["ok"] is True
    for subject in (
        "mathematics",
        "physics",
        "chemistry",
        "biology",
        "geography",
        "history",
        "english",
        "environmental_science",
    ):
        assert subject in health["subjects"]


def test_load_golden_prefers_topic_match():
    g = load_golden(subject="biology", topic="Photosynthesis")
    assert g is not None
    assert "photo" in str(g.get("topic") or "").lower() or "photo" in str(g.get("id") or "")
