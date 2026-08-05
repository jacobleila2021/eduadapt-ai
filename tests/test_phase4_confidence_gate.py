"""Phase 4 — One-Generate confidence gate."""

from __future__ import annotations

from engines.lesson_composition_engine.confidence_gate import (
    confidence_block_reason,
    confidence_gate_issues,
)
from publication_gate import publication_block_reason


def _pkg(**overrides):
    base = {
        "_lesson_wall": [
            {
                "title": "Evaporation",
                "idea": "Evaporation is when liquid water turns into water vapour and rises.",
            },
            {
                "title": "Condensation",
                "idea": "Condensation is when water vapour cools into tiny liquid droplets.",
            },
        ],
        "standard": {
            "topic": "The Water Cycle",
            "lesson_wall": [
                {
                    "title": "Evaporation",
                    "idea": "Evaporation is when liquid water turns into water vapour and rises.",
                },
                {
                    "title": "Condensation",
                    "idea": "Condensation is when water vapour cools into tiny liquid droplets.",
                },
            ],
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
            ],
            "svg_diagram": (
                '<svg xmlns="http://www.w3.org/2000/svg"><text>Evaporation</text></svg>'
            ),
        },
        "worksheet": {"short_answer": []},
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


def test_publication_gate_uses_confidence_gate():
    pkg = _pkg()
    pkg["standard"]["sections"][0]["body"] = "Important words: foo, bar."
    # fidelity may scrub first — ensure confidence still sees chrome if present on wall
    pkg["_lesson_wall"][0]["idea"] = "Evaporation (key word) means vapour rises."
    reason = publication_block_reason(pkg)
    assert reason
