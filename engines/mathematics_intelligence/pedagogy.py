"""Assessment / revision / accessibility / teaching-strategy metadata for MIP."""

from __future__ import annotations

from typing import Any

from engines.subject_intelligence_core.accessibility import build_accessibility_guidance
from engines.subject_intelligence_core.assessment import (
    build_assessment_hints,
    build_revision_summary,
)
from engines.subject_intelligence_core.pedagogy import build_teaching_strategies
from engines.subject_intelligence_core.tutor_metadata import (
    error_diagnosis_block,
    graduated_hints_block,
    reflection_block,
    socratic_block,
    worked_example_fading_block,
)

TEACHING_FRAMEWORKS: tuple[dict[str, str], ...] = (
    {"id": "cra", "name": "Concrete–Representational–Abstract"},
    {"id": "explicit_instruction", "name": "Explicit Instruction"},
    {"id": "gradual_release", "name": "Gradual Release of Responsibility"},
    {"id": "productive_struggle", "name": "Productive Struggle"},
    {"id": "retrieval_practice", "name": "Retrieval Practice"},
    {"id": "interleaving", "name": "Interleaving"},
    {"id": "spaced_practice", "name": "Spaced Practice"},
    {"id": "multiple_representations", "name": "Multiple Representations"},
)


def teaching_strategies(domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return build_teaching_strategies(
        TEACHING_FRAMEWORKS,
        domains,
        provenance="mathematics_intelligence.teaching",
        default_domain="arithmetic",
        application_template="Apply {name} while teaching {primary} concepts from the lesson.",
    )


def assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return build_assessment_hints(
        uli,
        domains,
        provenance="mathematics_intelligence.assessment",
        default_domain="general",
    )


def revision_summary(domains: list[dict[str, Any]], misconceptions: list[dict[str, Any]]) -> dict[str, Any]:
    return build_revision_summary(
        domains,
        misconceptions,
        retrieval_prompts=[
            "State the key rule from today's lesson in one sentence.",
            "Solve a near-transfer problem using the same property.",
            "Explain a common mistake and how to avoid it.",
        ],
        provenance="mathematics_intelligence.revision",
    )


def accessibility_guidance(uli: Any) -> list[dict[str, Any]]:
    return build_accessibility_guidance(
        [
            {
                "recommendation": "dyslexia_friendly_notation",
                "detail": "Prefer spaced operators, avoid dense stacked fractions in running text; offer linear form.",
                "owner": "AIE",
            },
            {
                "recommendation": "symbol_glossary",
                "detail": "Provide plain-language gloss for symbols (=, ≠, ≤, √, ∠) used in the lesson.",
                "owner": "AIE",
            },
            {
                "recommendation": "read_aloud_equations",
                "detail": "Expose equation reading order for TTS (left-to-right with spoken operators).",
                "owner": "VMLE/AIE",
            },
            {
                "recommendation": "colour_safe_highlight",
                "detail": "Highlight like terms with patterns/shapes, not colour alone.",
                "owner": "AIE",
            },
            {
                "recommendation": "chunk_multi_step",
                "detail": "Split multi-step solutions into 2–4 visible chunks to reduce cognitive load.",
                "owner": "AIE",
            },
            {
                "recommendation": "cognitive_load_reduction",
                "detail": "Show one representation at a time before combining CRA modes.",
                "owner": "AIE",
            },
        ],
        uli,
        attach_reading_band_to="chunk_multi_step",
    )


def tutor_guidance(misconceptions: list[dict[str, Any]], scaffolds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        socratic_block(
            [
                "What is given, and what are you trying to find?",
                "Which lesson rule lets you transform this expression?",
                "How would you check that both sides still match?",
            ]
        ),
        graduated_hints_block(
            [
                "Hint 1: Name the operation family (add/multiply/inverse).",
                "Hint 2: Point to the relevant worked-example step without revealing the answer.",
                "Hint 3: Offer a isomorphic simpler numerical case.",
            ]
        ),
        worked_example_fading_block(scaffolds),
        error_diagnosis_block(misconceptions),
        reflection_block(
            [
                "Which step was hardest, and why?",
                "Where might a sign error creep in?",
            ]
        ),
    ]


def lxp_interaction_hints(visuals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {"hook_id": "interactive_graphs", "visual_types": [v["visual_type"] for v in visuals if "plot" in v.get("visual_type", "") or "coordinate" in v.get("visual_type", "")]},
        {"hook_id": "equation_walkthroughs", "detail": "Step cards bound to worked-example scaffolds"},
        {"hook_id": "formula_cards", "detail": "Flashcards for lesson formulae (source-linked)"},
        {"hook_id": "concept_maps", "detail": "Domain prerequisite map"},
        {"hook_id": "practice_widgets", "detail": "Low-stakes retrieval items (AME generates items)"},
        {"hook_id": "revision_summaries", "detail": "Spaced practice checklist"},
        *[
            {"hook_id": "recommended_visual", "visual_type": v.get("visual_type"), "label": v.get("label")}
            for v in visuals[:6]
        ],
    ]
