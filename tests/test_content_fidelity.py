"""Phase Final — Content Fidelity & Publishing Recovery tests."""

from __future__ import annotations

from engines.lesson_composition_engine.content_fidelity import (
    CONTENT_FIDELITY_PUBLISHING_RECOVERY_SMOKE_OK,
    apply_content_fidelity,
    content_fidelity_block_reason,
    content_fidelity_issues,
    prompt_leak_hits,
    simplify_vocab_card,
)
from publication_gate import publication_allowed, publication_block_reason


def test_content_fidelity_smoke():
    assert CONTENT_FIDELITY_PUBLISHING_RECOVERY_SMOKE_OK is True


def test_prompt_leak_detection_and_scrub():
    dirty = {
        "standard": {
            "big_idea": "Using the uploaded source, Pressure equals force over area.",
            "sections": [
                {
                    "title": "Concept",
                    "role": "concept",
                    "body": "Prompt: Explain pressure. Metadata: Grade Level 8. Force on an area is pressure.",
                },
                {
                    "title": "Summary",
                    "role": "summary",
                    "body": "You can explain the key ideas now. Check one example, then take a short pause before you revise.",
                },
            ],
            "flowchart_svg": "<svg xmlns='http://www.w3.org/2000/svg'><text>Pressure</text></svg>",
        },
        "adhd": {
            "sections": [
                {"title": "Mission", "role": "hook", "body": "Two-minute mission: define pressure with one example."},
            ]
        },
        "vocabulary": {
            "word_wall": [
                {
                    "term": "Pressure",
                    "definition": "Force on an area.",
                    "pronunciation": "presh-er",
                    "part_of_speech": "noun",
                    "audio_label": "Listen: Pressure",
                }
            ]
        },
    }
    assert prompt_leak_hits(dirty["standard"]["big_idea"])
    cleaned = apply_content_fidelity(dirty, board={"topic": "Force and Pressure"})
    blob = " ".join(
        str(s.get("body") or "") for s in cleaned["standard"]["sections"] if isinstance(s, dict)
    ).lower()
    assert "using the uploaded source" not in blob
    assert "prompt:" not in blob
    assert "metadata" not in blob
    wall = cleaned["vocabulary"]["word_wall"][0]
    assert not wall.get("pronunciation")
    assert not wall.get("part_of_speech")
    assert wall.get("student_flashcard") is True
    summary = next(s for s in cleaned["standard"]["sections"] if s.get("role") == "summary")
    assert "check one example, then take a short pause" not in summary["body"].lower()
    assert not content_fidelity_issues(cleaned)


def test_publication_gate_blocks_prompt_leaks():
    leaked = {
        "standard": {
            "sections": [
                {"title": "A", "role": "concept", "body": "Using the uploaded source, learn force."},
            ]
        }
    }
    reason = content_fidelity_block_reason(leaked)
    assert reason
    assert not publication_allowed(leaked)
    assert "Content fidelity" in publication_block_reason(leaked)


def test_student_flashcard_shape():
    card = simplify_vocab_card(
        {
            "term": "Force",
            "definition": "A push or a pull.",
            "pronunciation": "fors",
            "part_of_speech": "noun",
            "audio_label": "Listen: Force",
        },
        topic="Force and Pressure",
    )
    assert card["term"] == "FORCE"
    assert card["pronunciation"] == ""
    assert "Meaning" not in card["definition"]  # meaning text only
    assert card["remember_this"]
    assert card["use_this_word"]
