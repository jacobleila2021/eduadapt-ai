"""Phase 4 — One-Generate confidence gate (includes Phase 1 wall freeze)."""

from __future__ import annotations

from engines.lesson_composition_engine.confidence_gate import (
    confidence_block_reason,
    confidence_gate_issues,
)
from publication_gate import publication_block_reason


def _wall_triple():
    return [
        {
            "title": "Evaporation",
            "idea": "Evaporation is when liquid water turns into water vapour and rises.",
        },
        {
            "title": "Condensation",
            "idea": "Condensation is when water vapour cools into tiny liquid droplets.",
        },
        {
            "title": "Precipitation",
            "idea": "Precipitation is water that falls from clouds as rain, snow, sleet, or hail.",
        },
    ]


def _pkg(**overrides):
    wall = _wall_triple()
    base = {
        "_lesson_wall": wall,
        "standard": {
            "topic": "The Water Cycle",
            "lesson_wall": list(wall),
            "svg_diagram": (
                '<svg xmlns="http://www.w3.org/2000/svg"><text>Evaporation</text>'
                "<text>Collection</text></svg>"
            ),
            "sections": [
                {
                    "role": "concept",
                    "title": "Evaporation",
                    "body": "Evaporation is when liquid water turns into water vapour and rises.",
                }
            ],
        },
        "ell": {"lesson_wall": list(wall), "topic": "The Water Cycle"},
        "parent": {"lesson_wall": list(wall), "topic": "The Water Cycle"},
        "vocabulary": {
            "word_wall": [
                {
                    "term": "Evaporation",
                    "definition": "Evaporation is when liquid water turns into water vapour and rises.",
                },
                {
                    "term": "Condensation",
                    "definition": "Condensation is when water vapour cools into tiny liquid droplets.",
                },
                {
                    "term": "Precipitation",
                    "definition": "Precipitation is water that falls from clouds as rain, snow, sleet, or hail.",
                },
            ],
            "svg_diagram": (
                '<svg xmlns="http://www.w3.org/2000/svg"><text>Evaporation</text></svg>'
            ),
        },
        "worksheet": {
            "long_answer": [
                {
                    "question": "Explain Evaporation",
                    "model_answer": "Evaporation is when liquid water turns into water vapour and rises.",
                    "source": "lesson_wall",
                }
            ],
            "short_answer": [],
        },
        "_stem_artifacts": [],
        "_meta": {},
    }
    base.update(overrides)
    return base


def test_confidence_gate_passes_wall_aligned_package():
    assert confidence_block_reason(_pkg()) == ""


def test_confidence_gate_blocks_key_word_chrome():
    pkg = _pkg()
    pkg["standard"]["sections"][0]["body"] = "Evaporation (key word) is liquid to vapour."
    reason = confidence_block_reason(pkg)
    assert "key word" in reason.lower() or "chrome" in reason.lower()


def test_confidence_gate_blocks_thin_wall_without_stem():
    pkg = _pkg(_lesson_wall=[], standard={"topic": "X", "sections": [], "lesson_wall": []})
    issues = confidence_gate_issues(pkg)
    assert any("Lesson Wall" in i for i in issues)


def test_confidence_gate_blocks_recycled_wall_sentences():
    clone = "Evaporation is when liquid water turns into water vapour and rises."
    pkg = _pkg(
        _lesson_wall=[
            {"title": "One", "idea": clone},
            {"title": "Two", "idea": clone},
            {"title": "Three", "idea": clone},
        ]
    )
    issues = confidence_gate_issues(pkg)
    assert any("recycles" in i.lower() for i in issues)


def test_publication_gate_uses_confidence_gate():
    pkg = _pkg()
    pkg["standard"]["sections"][0]["body"] = "Important words: foo, bar."
    pkg["_lesson_wall"][0]["idea"] = "Evaporation (key word) means vapour rises into the open air."
    reason = publication_block_reason(pkg)
    assert reason


def test_confidence_gate_repairs_missing_wall_stamps_after_polish():
    """PQLE can rebuild ell/parent/visual without lesson_wall — must not quarantine."""
    pkg = _pkg()
    # Simulate polish dropping wall stamps on lenses (sample-lesson failure mode).
    for key in ("ell", "parent", "visual"):
        pkg[key] = {"topic": "The Water Cycle", "sections": [{"role": "concept", "title": "X", "body": "Y" * 40}]}
    assert confidence_block_reason(pkg) == ""
    for key in ("ell", "parent", "visual"):
        assert pkg[key].get("lesson_wall"), f"{key} must be re-stamped"
    reason = publication_block_reason(pkg)
    assert "Confidence gate" not in reason
    assert "missing the shared Lesson Wall" not in reason
