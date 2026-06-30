"""Smoke tests for audio learning controls and adaptation validation."""

from audio_learning import VOICE_OPTIONS, split_sentences
from ai_generator import _adaptation_difference_score, _valid_lesson


def test_narration_excludes_labels_and_markup():
    from audio_learning import build_narration

    lesson = {
        "big_idea": "Water moves in a cycle.",
        "sections": [
            {"title": "Evaporation", "body": "<div style='color:#000'>The sun heats water.</div>"},
            {"title": "Diagram", "body": "<svg><rect/></svg>"},
        ],
    }
    text = build_narration(lesson, "standard")
    assert "Water moves in a cycle." in text
    assert "The sun heats water." in text
    # No HTML/SVG markup or adaptation labels leak into narration
    assert "<" not in text and ">" not in text
    assert "svg" not in text.lower()
    assert "Neurodiversity" not in text


def test_narration_vocabulary_reads_definitions_only():
    from audio_learning import build_narration

    vocab = {
        "word_wall": [
            {"term": "Evaporation", "definition": "Water turning into vapour.", "example": "Puddles dry up."}
        ]
    }
    text = build_narration(vocab, "vocabulary")
    assert "Evaporation" in text
    assert "Water turning into vapour." in text
    assert "Word Wall" not in text
    assert "Front" not in text and "Back" not in text


def test_fallback_lesson_diagram_is_real_svg():
    from structured_renderers import _fallback_lesson_diagram, _valid_svg_diagram

    lesson = {
        "topic": "Water Cycle",
        "sections": [{"title": "Evaporation"}, {"title": "Condensation"}, {"title": "Precipitation"}],
    }
    svg = _fallback_lesson_diagram(lesson)
    assert _valid_svg_diagram(svg)
    assert "Evaporation" in svg


def test_fill_blank_answer_extraction():
    from structured_renderers import _extract_blank_answer, _resolve_fill_blank_answer

    display, ans = _extract_blank_answer(
        "The distance from the center to the edge of a circle is called the _____ (radius)."
    )
    assert ans == "radius"
    assert "(radius)" not in display

    word_wall = [{"term": "radius", "definition": "Distance from center to edge."}]
    _, resolved = _resolve_fill_blank_answer(
        "The distance from the center to the edge of a circle is called the _____ (radius).",
        1,
        {"fill_blank_answers": ["radius"]},
        word_wall,
    )
    assert resolved == "radius"

    _, from_bracket = _resolve_fill_blank_answer(
        "A _____ is used to draw circles (compass).",
        1,
        {},
        [{"term": "compass", "definition": "Tool to draw circles."}],
    )
    assert from_bracket == "compass"


def test_indian_voices_present():
    from audio_learning import VOICE_OPTIONS

    assert "Warm Female (Indian)" in VOICE_OPTIONS
    assert "Warm Male (Indian)" in VOICE_OPTIONS


def test_male_voice_avoids_female():
    from audio_learning import VOICE_OPTIONS

    assert "female" in VOICE_OPTIONS["Warm Male (International)"]["avoid"]
    # Warm Male hints must not contain bare "male" (which matches "female")
    assert "male" not in VOICE_OPTIONS["Warm Male (International)"]["hints"]


def test_voices_have_instructions():
    from audio_learning import VOICE_OPTIONS

    for label, meta in VOICE_OPTIONS.items():
        assert meta.get("instructions"), f"{label} missing TTS instructions"
        assert meta.get("openai"), f"{label} missing OpenAI voice"


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


def test_lesson_design_variants():
    from lesson_design import BG_MAIN, TEXT_BODY, accent_for_variant, classify_section

    assert BG_MAIN == "#FFF9EE"
    assert TEXT_BODY == "#333333"
    assert classify_section("Welcome to today's lesson", "", 0) == "introduction"
    assert classify_section("Explain the water cycle", "teal", 1) == "information"
    assert classify_section("Creative story time", "orange", 2) == "stories"
    assert accent_for_variant("introduction") == "#059669"


def test_nine_version_tabs():
    from navigation import PILL_CATEGORIES

    labels = [c["label"] for c in PILL_CATEGORIES]
    assert labels == [
        "Vocabulary Support",
        "Mainstream Support",
        "Neurodiversity Support",
        "English Language Support",
        "Visual Learner Support",
        "Auditory Learner Support",
        "Teacher Version",
        "Parent Version",
        "Exam Worksheet",
    ]
    # Each tab maps to exactly one version (no sub-classification pills)
    for cat in PILL_CATEGORIES:
        assert len(cat["spec_ids"]) == 1


def test_only_nine_generated():
    from adaptation_specs import OUTPUT_KEYS

    assert len(OUTPUT_KEYS) == 9
    assert set(OUTPUT_KEYS) == {
        "vocabulary", "standard", "ld", "ell", "visual",
        "auditory", "teacher", "parent", "worksheet",
    }


def test_title_drops_how_subtitle():
    from workspace_page import _clean_title

    assert _clean_title("The Water Cycle: How Water Moves") == "The Water Cycle"
    assert _clean_title("Photosynthesis") == "Photosynthesis"


def test_warm_voices_only():
    assert set(VOICE_OPTIONS.keys()) == {
        "Warm Female (International)",
        "Warm Male (International)",
        "Warm Female (Indian)",
        "Warm Male (Indian)",
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
