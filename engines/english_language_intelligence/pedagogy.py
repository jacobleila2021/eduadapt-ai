"""ELIP pedagogy, visuals, tutor, companion, and LXP metadata via SICS."""

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
    {"id": "inquiry", "name": "Inquiry-Based Learning"},
    {"id": "guided_discovery", "name": "Guided Discovery"},
    {"id": "socratic", "name": "Socratic Learning"},
    {"id": "cra", "name": "Concrete–Representational–Abstract"},
    {"id": "worked_examples", "name": "Worked Examples"},
    {"id": "retrieval_practice", "name": "Retrieval Practice"},
    {"id": "spaced_practice", "name": "Spaced Practice"},
    {"id": "reflection", "name": "Reflection"},
    {"id": "collaborative", "name": "Collaborative Learning"},
    {"id": "direct_instruction", "name": "Direct Instruction"},
)

VISUAL_CATALOGUE: dict[str, list[dict[str, str]]] = {
    "reading": [
        {"visual_type": "reading_mode", "label": "Focused reading mode"},
        {"visual_type": "annotation_pane", "label": "Inline literary annotations"},
    ],
    "vocabulary": [
        {"visual_type": "vocabulary_cards", "label": "Vocabulary revision cards"},
        {"visual_type": "click_to_define", "label": "Click-to-define"},
        {"visual_type": "click_to_pronounce", "label": "Click-to-pronounce"},
    ],
    "grammar": [
        {"visual_type": "sentence_diagram", "label": "Sentence structure diagram"},
        {"visual_type": "editing_checklist", "label": "Editing checklist"},
    ],
    "writing": [
        {"visual_type": "essay_organiser", "label": "Essay organisation map"},
        {"visual_type": "paragraph_frame", "label": "Paragraph frame"},
    ],
    "literature": [
        {"visual_type": "literary_annotation", "label": "Literary annotation layer"},
        {"visual_type": "character_map", "label": "Character map"},
        {"visual_type": "plot_diagram", "label": "Plot diagram"},
    ],
    "speaking": [
        {"visual_type": "pronunciation_playback", "label": "Pronunciation playback"},
        {"visual_type": "conversation_prompt_cards", "label": "Conversation prompt cards"},
    ],
    "listening": [
        {"visual_type": "audio_comprehension", "label": "Listening comprehension player"},
    ],
    "pronunciation": [
        {"visual_type": "pronunciation_playback", "label": "Pronunciation playback"},
        {"visual_type": "click_to_pronounce", "label": "Click-to-pronounce"},
    ],
}


def teaching_strategies(domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return build_teaching_strategies(
        TEACHING_FRAMEWORKS,
        domains,
        provenance="english_language_intelligence.teaching",
        default_domain="reading",
        application_template="Apply {name} while teaching {primary} from the verified lesson.",
    )


def recommend_visuals(text: str, domains: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    from engines.english_language_intelligence.domains import detect_domains

    domains = domains if domains is not None else detect_domains(text)
    return recommend_visuals_from_catalogue(
        domains,
        VISUAL_CATALOGUE,
        provenance="english_language_intelligence.visuals",
        limit=10,
        default_visual={"visual_type": "reading_mode", "label": "Reading mode"},
    )


def assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    practices = (
        "reading_comprehension",
        "vocabulary_mastery",
        "grammar_objectives",
        "writing_competencies",
        "speaking_competencies",
        "listening_competencies",
    )

    def extra(i: int, _text: str | None) -> dict[str, Any]:
        return {
            "language_competency": practices[i % len(practices)],
            "rubric_mapping_hint": "Map to lesson rubric criteria when present in source.",
        }

    return build_assessment_hints(
        uli,
        domains,
        provenance="english_language_intelligence.assessment",
        default_domain="reading",
        extra_fields=extra,
    )


def revision_summary(domains: list[dict[str, Any]], misconceptions: list[dict[str, Any]]) -> dict[str, Any]:
    return build_revision_summary(
        domains,
        misconceptions,
        retrieval_prompts=[
            "Retell the main idea with two supporting details.",
            "Use three lesson vocabulary words in original sentences.",
            "Revise one paragraph for clarity and cohesion.",
        ],
        provenance="english_language_intelligence.revision",
    )


def accessibility_guidance(uli: Any) -> list[dict[str, Any]]:
    return build_accessibility_guidance(
        [
            {
                "recommendation": "simplified_english",
                "detail": "Offer plain-language paraphrases beside dense academic sentences.",
                "owner": "AIE",
            },
            {
                "recommendation": "reading_level_adaptation",
                "detail": "Chunk long passages; highlight key sentences for guided reading.",
                "owner": "AIE",
            },
            {
                "recommendation": "dyslexia_support",
                "detail": "Prefer dyslexia-friendly fonts/spacing; avoid dense justified blocks.",
                "owner": "AIE",
            },
            {
                "recommendation": "adhd_support",
                "detail": "Short reading goals with visible progress checkpoints.",
                "owner": "AIE",
            },
            {
                "recommendation": "executive_function_support",
                "detail": "Provide checklists for planning, drafting, and revising writing tasks.",
                "owner": "AIE",
            },
            {
                "recommendation": "ell_guidance",
                "detail": "Pre-teach tier-2 vocabulary; allow bilingual gloss where policy permits.",
                "owner": "AIE",
            },
            {
                "recommendation": "vocabulary_scaffolds",
                "detail": "Inline click-to-define and example-from-source cards.",
                "owner": "AIE/LXP",
            },
            {
                "recommendation": "audio_first_presentation",
                "detail": "Offer VMLE read-aloud for passages and vocabulary.",
                "owner": "VMLE/AIE",
            },
            {
                "recommendation": "cognitive_load_reduction",
                "detail": "One literacy focus at a time (e.g. vocabulary before close reading).",
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
                "What is the text mostly about?",
                "Which words or phrases are evidence for your claim?",
                "How would you explain this idea to a classmate?",
            ]
        ),
        custom_mode_block(
            "reading_prompts",
            prompts=[
                "Predict what might come next and why.",
                "Whose point of view is this, and how do you know?",
            ],
        ),
        custom_mode_block(
            "discussion_prompts",
            prompts=[
                "Do you agree with the author's purpose? Support with evidence.",
            ],
        ),
        custom_mode_block(
            "writing_hints",
            levels=[
                "Hint 1: Name your purpose and audience.",
                "Hint 2: Place a controlling idea at the opening of the paragraph.",
                "Hint 3: Add one lesson-based piece of evidence, then explain it.",
            ],
        ),
        custom_mode_block(
            "vocabulary_coaching",
            prompts=[
                "Use context clues before looking up the word.",
                "Try the word in a new sentence that keeps the lesson meaning.",
            ],
        ),
        graduated_hints_block(
            [
                "Hint 1: Locate the key sentence.",
                "Hint 2: Underline supporting details.",
                "Hint 3: Paraphrase without copying whole sentences.",
            ]
        ),
        error_diagnosis_block(misconceptions),
        reflection_block(
            [
                "Which strategy helped most: predicting, annotating, or summarising?",
                "What will you revise in your next draft?",
            ]
        ),
    ]


def companion_metadata(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "owner": "ALCIS",
        "behaviours": [
            {"id": "celebrate_reading_milestones", "when": "reading_goal_complete"},
            {"id": "encourage_writing_practice", "when": "writing_domain_active"},
            {"id": "recommend_revision", "when": "draft_submitted"},
            {"id": "suggest_vocabulary_review", "when": "tier2_terms_present"},
            {"id": "promote_healthy_reading_habits", "when": "session_end"},
        ],
        "active_domains": [d["domain"] for d in domains[:4]],
        "provenance": "english_language_intelligence.companion",
    }


def lxp_hints(visuals: list[dict[str, Any]], vocabulary: dict[str, Any]) -> list[dict[str, Any]]:
    types = {v.get("visual_type") for v in visuals}
    return [
        {"hook_id": "click_to_define", "available": "click_to_define" in types or bool(vocabulary.get("entries"))},
        {"hook_id": "click_to_pronounce", "available": "click_to_pronounce" in types or "pronunciation_playback" in types},
        {"hook_id": "inline_vocabulary", "available": bool(vocabulary.get("entries"))},
        {"hook_id": "literary_annotations", "available": "literary_annotation" in types},
        {"hook_id": "reading_mode", "available": "reading_mode" in types},
        {"hook_id": "pronunciation_playback", "available": "pronunciation_playback" in types},
        {"hook_id": "reading_goals", "available": True},
        {"hook_id": "vocabulary_revision_cards", "available": "vocabulary_cards" in types},
        *[
            {"hook_id": "recommended_visual", "visual_type": v.get("visual_type"), "label": v.get("label")}
            for v in visuals[:6]
        ],
    ]
