"""WLIP pedagogy, visuals, tutor, companion, LXP metadata via SICS."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.accessibility import build_accessibility_guidance
from engines.subject_intelligence_core.assessment import (
    build_assessment_hints,
    build_revision_summary,
)
from engines.subject_intelligence_core.diagrams import recommend_visuals_from_catalogue
from engines.subject_intelligence_core.pedagogy import build_teaching_strategies
from engines.subject_intelligence_core.tutor_metadata import (
    custom_mode_block,
    error_diagnosis_block,
    graduated_hints_block,
    reflection_block,
    socratic_block,
)

TEACHING_FRAMEWORKS: tuple[dict[str, str], ...] = (
    {"id": "communicative", "name": "Communicative Language Teaching"},
    {"id": "task_based", "name": "Task-Based Language Teaching"},
    {"id": "input_rich", "name": "Comprehensible Input"},
    {"id": "form_focus", "name": "Focus on Form"},
    {"id": "spaced_practice", "name": "Spaced Practice"},
    {"id": "retrieval_practice", "name": "Retrieval Practice"},
    {"id": "extensive_reading", "name": "Extensive Reading"},
    {"id": "guided_discovery", "name": "Guided Discovery"},
    {"id": "socratic", "name": "Socratic Dialogue"},
    {"id": "reflection", "name": "Reflection"},
)

VISUAL_CATALOGUE: dict[str, list[dict[str, str]]] = {
    "phonetics": [
        {"visual_type": "ipa_chart", "label": "IPA chart"},
        {"visual_type": "script_panel", "label": "Script panel"},
    ],
    "pronunciation": [
        {"visual_type": "pronunciation_waveform", "label": "Pronunciation waveform"},
        {"visual_type": "minimal_pair_cards", "label": "Minimal pair cards"},
        {"visual_type": "ipa_viewer", "label": "IPA viewer"},
    ],
    "grammar": [
        {"visual_type": "grammar_panel", "label": "Grammar panel"},
        {"visual_type": "sentence_pattern_map", "label": "Sentence pattern map"},
    ],
    "vocabulary": [
        {"visual_type": "vocabulary_popup", "label": "Vocabulary popup"},
        {"visual_type": "word_family_map", "label": "Word family map"},
    ],
    "reading": [
        {"visual_type": "read_along", "label": "Read-along view"},
        {"visual_type": "paragraph_structure", "label": "Paragraph structure"},
    ],
    "writing": [
        {"visual_type": "essay_outline", "label": "Essay outline scaffold"},
        {"visual_type": "cohesion_checklist", "label": "Cohesion checklist"},
    ],
    "speaking": [
        {"visual_type": "dialogue_cards", "label": "Dialogue cards"},
        {"visual_type": "speaking_recorder", "label": "Speaking recorder"},
    ],
    "listening": [
        {"visual_type": "audio_player", "label": "Adjustable audio player"},
    ],
    "culture": [
        {"visual_type": "culture_notes", "label": "Culture notes panel"},
        {"visual_type": "idiom_cards", "label": "Idiom cards"},
    ],
    "translation": [
        {"visual_type": "translation_drawer", "label": "Translation drawer"},
    ],
    "literature": [
        {"visual_type": "literary_device_panel", "label": "Literary device panel"},
        {"visual_type": "plot_map", "label": "Plot map"},
    ],
}


def teaching_strategies(domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return build_teaching_strategies(
        TEACHING_FRAMEWORKS,
        domains,
        provenance="world_languages_intelligence.teaching",
        default_domain="vocabulary",
        application_template="Apply {name} while teaching {primary} from the verified lesson.",
    )


def recommend_visuals(text: str, domains: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    from engines.world_languages_intelligence.domains import detect_domains

    domains = domains if domains is not None else detect_domains(text)
    return recommend_visuals_from_catalogue(
        domains,
        VISUAL_CATALOGUE,
        provenance="world_languages_intelligence.visuals",
        limit=10,
        default_visual={"visual_type": "vocabulary_popup", "label": "Vocabulary support"},
    )


def assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    practices = (
        "vocabulary_quizzes",
        "reading_comprehension",
        "listening",
        "speaking",
        "grammar",
        "writing",
        "oral_assessment",
        "rubrics",
    )

    def extra(i: int, _text: str | None) -> dict[str, Any]:
        return {
            "language_practice": practices[i % len(practices)],
            "reveals_answers": False,
        }

    return build_assessment_hints(
        uli,
        domains,
        provenance="world_languages_intelligence.assessment",
        default_domain="vocabulary",
        extra_fields=extra,
    )


def revision_summary(domains: list[dict[str, Any]], misconceptions: list[dict[str, Any]]) -> dict[str, Any]:
    return build_revision_summary(
        domains,
        misconceptions,
        retrieval_prompts=[
            "Produce three target words from the lesson with example sentences (from lesson sense).",
            "Explain one grammar pattern with a short example from the lesson.",
            "Practise one pronunciation focus (stress, tone, or minimal pair) from the lesson.",
        ],
        provenance="world_languages_intelligence.revision",
    )


def accessibility_guidance(uli: Any) -> list[dict[str, Any]]:
    return build_accessibility_guidance(
        [
            {
                "recommendation": "dyslexia_friendly_reading",
                "detail": "Increase spacing; offer dyslexia-friendly font; chunk lines.",
                "owner": "AIE/LXP",
            },
            {
                "recommendation": "read_along",
                "detail": "Highlight words as VMLE narrates.",
                "owner": "VMLE/AIE",
            },
            {
                "recommendation": "simplified_vocabulary",
                "detail": "Gloss high-frequency and lesson-critical terms.",
                "owner": "AIE",
            },
            {
                "recommendation": "audio_narration",
                "detail": "Provide audio for reading passages and dialogues.",
                "owner": "VMLE",
            },
            {
                "recommendation": "adjustable_pacing",
                "detail": "Allow slower playback for listening tasks.",
                "owner": "VMLE/LXP",
            },
            {
                "recommendation": "script_support",
                "detail": "Show script/romanisation options where the lesson provides them.",
                "owner": "AIE/LXP",
            },
            {
                "recommendation": "high_contrast",
                "detail": "High-contrast text and IPA/script panels.",
                "owner": "AIE",
            },
            {
                "recommendation": "font_selection",
                "detail": "Learner-selectable fonts for Latin and complex scripts.",
                "owner": "AIE/LXP",
            },
            {
                "recommendation": "cognitive_load_reduction",
                "detail": "Separate form focus from meaning-focused tasks.",
                "owner": "AIE",
            },
        ],
        uli,
        attach_reading_band_to="cognitive_load_reduction",
    )


def tutor_guidance(misconceptions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        socratic_block(
            [
                "What meaning are you trying to express?",
                "Which pattern from the lesson matches that meaning?",
                "How would a listener know you meant that?",
            ]
        ),
        custom_mode_block(
            "conversation_prompts",
            prompts=[
                "Reuse two lesson phrases in a short dialogue turn.",
            ],
        ),
        custom_mode_block(
            "vocabulary_hints",
            prompts=[
                "Use context clues before checking the glossary.",
            ],
        ),
        custom_mode_block(
            "grammar_hints",
            prompts=[
                "Identify the tense/agreement/case marker before rewriting.",
            ],
        ),
        custom_mode_block(
            "reading_strategies",
            prompts=[
                "Skim for gist, then scan for the target form.",
            ],
        ),
        graduated_hints_block(
            [
                "Hint 1: Notice the form highlighted in the lesson.",
                "Hint 2: Compare with a correct model sentence from the lesson.",
                "Hint 3: Produce a parallel sentence without revealing protected answers.",
            ]
        ),
        error_diagnosis_block(misconceptions),
        reflection_block(
            [
                "Which skill felt hardest: listening, speaking, reading, or writing?",
                "What pronunciation or vocabulary goal will you set for tomorrow?",
            ]
        ),
    ]


def companion_metadata(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "owner": "ALCIS",
        "behaviours": [
            {"id": "daily_language_goals", "when": "session_start"},
            {"id": "pronunciation_streaks", "when": "pronunciation_practice"},
            {"id": "vocabulary_achievements", "when": "vocab_threshold"},
            {"id": "reading_milestones", "when": "passage_complete"},
        ],
        "active_domains": [d["domain"] for d in domains[:4]],
        "provenance": "world_languages_intelligence.companion",
    }


def lxp_hints(visuals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    types = {v.get("visual_type") for v in visuals}
    return [
        {"hook_id": "click_pronunciation", "available": "pronunciation_waveform" in types or "ipa_viewer" in types},
        {"hook_id": "read_aloud", "available": "read_along" in types or True},
        {"hook_id": "vocabulary_popups", "available": "vocabulary_popup" in types or True},
        {"hook_id": "grammar_panels", "available": "grammar_panel" in types},
        {"hook_id": "translation_drawer", "available": "translation_drawer" in types},
        {"hook_id": "speaking_recorder", "available": "speaking_recorder" in types},
        {"hook_id": "pronunciation_waveform", "available": "pronunciation_waveform" in types},
        {"hook_id": "ipa_viewer", "available": "ipa_viewer" in types or "ipa_chart" in types},
        *[
            {"hook_id": "recommended_visual", "visual_type": v.get("visual_type"), "label": v.get("label")}
            for v in visuals[:6]
        ],
    ]
