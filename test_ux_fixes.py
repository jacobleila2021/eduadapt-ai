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


def test_vocabulary_flowchart_has_terms():
    from flowchart_builder import build_vocabulary_flowchart

    vocab = {
        "topic": "Plant Tissues",
        "picture_words": [
            {"term": "Meristematic", "draw_this": "Cells that divide"},
            {"term": "Epithelial", "draw_this": "Covers body surfaces"},
        ],
        "word_wall": [{"term": "Meristematic", "definition": "Dividing cells."}],
    }
    chart = build_vocabulary_flowchart(vocab)
    assert "flowchart" in chart.lower()
    assert "Meristematic" in chart
    assert "classDef hub" in chart
    assert "<br" not in chart
    assert '(["' not in chart


def test_lesson_flowchart_grouped():
    from flowchart_builder import build_lesson_flowchart

    lesson = {
        "topic": "Tissues",
        "sections": [
            {"title": "Meristematic Tissue", "body": "Plant cells that divide at growing tips."},
            {"title": "Epithelial Tissue", "body": "Animal tissue covering organs."},
        ],
    }
    chart = build_lesson_flowchart(lesson)
    assert "flowchart" in chart.lower()
    assert "Meristematic" in chart or "Epithelial" in chart


def test_study_flowchart_title_only():
    from flowchart_builder import build_study_flowchart

    lesson = {
        "topic": "Water Cycle",
        "sections": [
            {"title": "Evaporation", "body": "The sun heats water."},
            {"title": "Condensation", "body": "Vapour forms clouds."},
            {"title": "Precipitation", "body": "Rain falls."},
        ],
    }
    chart = build_study_flowchart(lesson)
    assert "flowchart" in chart.lower()
    assert "Evaporation" in chart
    assert " - " not in chart
    assert "stroke-width:3px" in chart


def test_bullet_body_formatting():
    from lesson_design import format_lesson_body_html

    body = "- Water turns to vapour.\n- Clouds form in the sky.\n- Rain falls down."
    html_out = format_lesson_body_html(body, bullet_mode=True)
    assert "alora-lesson-bullets" in html_out
    assert "Water turns to vapour." in html_out
    assert "<ul" in html_out


def test_lesson_prompt_bullets_for_ld_only():
    from ai_generator import _lesson_prompt

    ld_prompt = _lesson_prompt("ld", "Dyslexia Smart", "hint")
    auditory_prompt = _lesson_prompt("auditory", "Auditory", "hint")
    assert "bullet" in ld_prompt.lower()
    assert "full prose" in auditory_prompt.lower() or "NO bullet" in auditory_prompt
    assert _lesson_prompt("standard", "Mainstream", "hint").count("bullet") < ld_prompt.count("bullet")


def test_normalize_section_title_replaces_generic():
    from section_titles import normalize_section_title

    title = normalize_section_title("Core Concept 1", "Meristematic tissue divides rapidly at tips.")
    assert "Meristematic" in title
    assert normalize_section_title("Photosynthesis", "Plants make food.") == "Photosynthesis"


def test_visual_practice_qa_layout():
    from lesson_design import format_visual_practice_html

    body = "Q1. What is evaporation?\nA1. Water turning to vapour.\nQ2. What is condensation?\nA2. Vapour forming clouds."
    html_out = format_visual_practice_html(body)
    assert "Q1." in html_out
    assert "A1." in html_out
    assert "alora-practice-pair" in html_out


def test_fallback_lesson_diagram_is_real_svg():
    from structured_renderers import _fallback_lesson_diagram, _valid_svg_diagram

    lesson = {
        "topic": "Water Cycle",
        "sections": [{"title": "Evaporation"}, {"title": "Condensation"}, {"title": "Precipitation"}],
    }
    svg = _fallback_lesson_diagram(lesson)
    assert _valid_svg_diagram(svg)
    assert "Evaporation" in svg


def test_study_diagram_grouped_tissues():
    from study_diagram_builder import build_study_diagram_svg, svg_text_label_count

    lesson = {
        "topic": "Plant and Animal Tissues",
        "sections": [
            {
                "title": "Meristematic Tissue",
                "body": "Plant tissue made of cells that can divide. Found at growing tips.",
            },
            {
                "title": "Permanent Tissue",
                "body": "Plant tissue that has lost the ability to divide, including parenchyma and collenchyma.",
            },
            {
                "title": "Epithelial Tissue",
                "body": "Animal tissue that covers body surfaces and lines organs.",
            },
            {
                "title": "Connective Tissue",
                "body": "Animal tissue that connects and supports other tissues, such as blood and bone.",
            },
        ],
    }
    svg = build_study_diagram_svg(lesson)
    assert svg_text_label_count(svg) >= 6
    assert "Meristematic" in svg
    assert "Epithelial" in svg
    assert "Plant" in svg or "Animal" in svg


def test_study_diagram_extracts_list_labels():
    from study_diagram_builder import _extract_fact_labels

    labels = _extract_fact_labels(
        "Permanent tissues include parenchyma, collenchyma, and sclerenchyma.",
        "Permanent Tissue",
    )
    assert any("parenchyma" in label.lower() for label in labels)


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


def test_fill_blank_rejects_off_topic_answers():
    from structured_renderers import _prepare_self_test

    tissues_wall = [
        {"term": "Meristematic tissue", "definition": "Tissue with dividing cells."},
        {"term": "Parenchyma", "definition": "Storage tissue in plants."},
    ]
    st = _prepare_self_test(
        {
            "fill_blanks": [
                "The distance from the center to the edge of a circle is called the ________."
            ],
            "fill_blank_answers": ["radius"],
        },
        tissues_wall,
    )
    assert st["fill_blank_answers"][0].lower() != "radius"


def test_indian_voices_present():
    from audio_learning import VOICE_OPTIONS

    assert "Female" in VOICE_OPTIONS
    assert "Male" in VOICE_OPTIONS


def test_male_voice_avoids_female():
    from audio_learning import VOICE_OPTIONS

    assert "female" in VOICE_OPTIONS["Male"]["avoid"]
    assert "male" not in VOICE_OPTIONS["Male"]["hints"]


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
        "Dyslexia Smart",
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


def test_fill_blank_display_hides_answers():
    from structured_renderers import _clean_fill_blank_display

    raw = "Meristematic tissue has dividing cells. The vocabulary word is _____ (Meristematic tissue)."
    display = _clean_fill_blank_display(raw)
    assert "Meristematic tissue)" not in display
    assert "(" not in display
    assert "-----." not in display
    assert "________" in display


def test_matching_answer_is_compact():
    from structured_renderers import _build_matching_section

    wall = [
        {"term": "Term A", "definition": "Definition A."},
        {"term": "Term B", "definition": "Definition B."},
    ]
    section = _build_matching_section(wall)
    assert section["matching_terms"]
    assert section["matching_answer_key"]
    assert "term" not in section["matching_answer_key"][0]


def test_fill_blank_semantic_not_index():
    from structured_renderers import _prepare_self_test

    wall = [
        {
            "term": "Meristematic tissue",
            "definition": "Tissue made of cells that can divide repeatedly.",
        },
        {
            "term": "Xylem",
            "definition": "Vascular tissue that transports water and minerals upward.",
        },
    ]
    st = _prepare_self_test(
        {
            "fill_blanks": [
                "Meristematic tissue is made of cells that can ________.",
                "Xylem is responsible for transporting water and ________.",
            ],
            "fill_blank_answers": ["divide", "minerals"],
        },
        wall,
    )
    assert st["fill_blank_answers"][0] == "divide"
    assert st["fill_blank_answers"][1] == "minerals"


def test_prepare_self_test_has_six_questions():
    from structured_renderers import _clean_fill_blank_display, _prepare_self_test

    wall = [{"term": f"T{i}", "definition": f"Def {i}."} for i in range(1, 9)]
    st = _prepare_self_test({}, wall)
    assert len(st["fill_blanks"]) >= 6
    assert len(st["fill_blank_answers"]) == len(st["fill_blanks"])
    assert "(" not in _clean_fill_blank_display(st["fill_blanks"][0])


def test_practice_has_no_pronunciation():
    from structured_renderers import _clean_practice_blank, _prepare_practice

    wall = [{"term": "Meristematic tissue", "definition": "Dividing cells.", "example": "Meristematic tissue grows."}]
    items = _prepare_practice(wall, "Plants")
    assert items
    blank = _clean_practice_blank(items[0]["sentence_blank"])
    assert "/" not in blank
    assert "(6)" not in blank


def test_sanitize_builds_multiple_self_test_questions():
    from ai_generator import _sanitize_vocabulary

    vocab = {
        "word_wall": [
            {"term": f"Term{i}", "definition": f"Definition for term {i}."}
            for i in range(1, 9)
        ],
        "self_test": {"fill_blanks": ["Only one question _____ (Term1)."]},
    }
    cleaned = _sanitize_vocabulary(vocab)
    assert len(cleaned["self_test"]["fill_blanks"]) >= 6
    assert cleaned["self_test"]["fill_blank_answers"]


def test_warm_voices_only():
    assert set(VOICE_OPTIONS.keys()) == {"Female", "Male"}


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
    six_sections = [{}] * 6
    assert not _valid_lesson({"big_idea": "x", "sections": six_sections})
    assert _valid_lesson(
        {
            "big_idea": "x",
            "sections": six_sections,
            "mermaid_diagram": "flowchart TD\nA-->B",
        }
    )
