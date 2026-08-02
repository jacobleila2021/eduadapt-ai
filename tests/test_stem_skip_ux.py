"""STEM: clear learner-facing copy when computation is skipped."""

from __future__ import annotations

from engines.lesson_pipeline import process_lesson_stem


def test_ambiguous_stem_warning_is_actionable():
    out = process_lesson_stem(
        "Solve the following.\nBalance →\nPhotosynthesis is the process by which plants make food.",
        topic="Photosynthesis",
    )
    warnings = out.get("routing_warnings") or []
    assert warnings, "incomplete STEM fragments should surface a routing warning"
    blob = " ".join(
        f"{w.get('message', '')} {w.get('recovery', '')}" for w in warnings
    ).lower()
    assert "verify" in blob or "verified" in blob or "incomplete" in blob
    assert "equation" in blob or "expression" in blob
    assert any(w.get("learner_visible") for w in warnings)
