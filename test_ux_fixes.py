"""Smoke tests for audio learning controls and adaptation validation."""

from audio_learning import VOICE_OPTIONS, split_sentences
from ai_generator import _adaptation_difference_score, _valid_lesson


def test_ruler_colors_soft():
    from accessibility import RULER_COLORS

    assert set(RULER_COLORS.keys()) == {"Soft Yellow", "Soft Mint", "Soft Aqua", "Soft Peach"}


def test_general_learner_naming():
    from adaptation_specs import ADAPTATION_SPECS

    std = next(s for s in ADAPTATION_SPECS if s["id"] == "standard")
    assert std["tab"] == "General Learner"
    assert std["title"] == "General Learner"


def test_warm_voices_only():
    assert set(VOICE_OPTIONS.keys()) == {"Warm Female", "Warm Male"}


def test_split_sentences_minimum():
    text = "This is sentence one. This is sentence two. And a third."
    parts = split_sentences(text)
    assert len(parts) >= 2


def test_adaptation_difference_score():
    base = {
        "big_idea": "Water cycle basics",
        "sections": [{"title": "Intro", "body": "Rain falls and evaporates quickly."}],
        "mermaid_diagram": "flowchart TD\nA-->B",
        "svg_diagram": "<svg></svg>",
    }
    different = {
        "big_idea": "ADHD chunked water cycle",
        "sections": [
            {"title": "Step 1", "body": "Two minute chunk about evaporation only."},
            {"title": "Step 2", "body": "Movement break then condensation."},
        ],
        "mermaid_diagram": "flowchart LR\nX-->Y",
        "svg_diagram": "<svg><circle/></svg>",
    }
    score = _adaptation_difference_score(base, different)
    assert score >= 0.5


def test_valid_lesson_requires_diagram():
    assert not _valid_lesson({"big_idea": "x", "sections": [{}, {}, {}]})
    assert _valid_lesson(
        {
            "big_idea": "x",
            "sections": [{}, {}, {}],
            "mermaid_diagram": "flowchart TD\nA-->B",
        }
    )
