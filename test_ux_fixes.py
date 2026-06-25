"""Smoke tests for audio learning controls and adaptation validation."""

from audio_learning import VOICE_OPTIONS, split_sentences
from ai_generator import _adaptation_difference_score, _valid_lesson


def test_indian_voices_present():
    from audio_learning import VOICE_OPTIONS

    assert "Indian Female Professional" in VOICE_OPTIONS
    assert "Indian Male Professional" in VOICE_OPTIONS


def test_male_voice_avoids_female():
    from audio_learning import VOICE_OPTIONS

    assert "female" in VOICE_OPTIONS["Warm Male"]["avoid"]
    # Warm Male hints must not contain bare "male" (which matches "female")
    assert "male" not in VOICE_OPTIONS["Warm Male"]["hints"]


def test_valid_mermaid_guard():
    from structured_renderers import _valid_mermaid

    assert _valid_mermaid("flowchart TD\nA-->B")
    assert not _valid_mermaid("")
    assert not _valid_mermaid("just some text")


def test_valid_svg_guard():
    from structured_renderers import _valid_svg_diagram

    good = "<svg width='200' height='100'><rect x='1' y='1' width='5' height='5'/><text>Sun</text></svg>"
    assert _valid_svg_diagram(good)
    assert not _valid_svg_diagram("<svg></svg>")
    assert not _valid_svg_diagram("")


def test_ruler_colors_soft():
    from accessibility import RULER_COLORS

    assert set(RULER_COLORS.keys()) == {"Soft Yellow", "Soft Mint", "Soft Aqua", "Soft Peach"}


def test_general_learner_naming():
    from adaptation_specs import ADAPTATION_SPECS

    std = next(s for s in ADAPTATION_SPECS if s["id"] == "standard")
    assert std["tab"] == "General Learner"
    assert std["title"] == "General Learner"


def test_warm_voices_only():
    assert "Warm Female" in VOICE_OPTIONS
    assert "Warm Male" in VOICE_OPTIONS
    assert set(VOICE_OPTIONS.keys()) == {
        "Warm Female",
        "Warm Male",
        "Indian Female Professional",
        "Indian Male Professional",
    }


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
