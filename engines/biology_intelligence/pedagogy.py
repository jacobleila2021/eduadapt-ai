"""Assessment / accessibility / teaching-strategy metadata for BIP."""

from __future__ import annotations

from typing import Any, Mapping

TEACHING_FRAMEWORKS: tuple[dict[str, str], ...] = (
    {"id": "inquiry", "name": "Inquiry-Based Learning"},
    {"id": "poe", "name": "Predict–Observe–Explain"},
    {"id": "cer", "name": "Claim–Evidence–Reasoning"},
    {"id": "concept_mapping", "name": "Concept Mapping"},
    {"id": "systems_thinking", "name": "Systems Thinking"},
    {"id": "structure_function", "name": "Structure–Function Relationships"},
    {"id": "cause_effect", "name": "Cause–Effect Analysis"},
    {"id": "scientific_investigation", "name": "Scientific Investigation"},
    {"id": "retrieval_practice", "name": "Retrieval Practice"},
)


def teaching_strategies(domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from engines.subject_intelligence_core.pedagogy import build_teaching_strategies

    return build_teaching_strategies(
        TEACHING_FRAMEWORKS,
        domains,
        provenance="biology_intelligence.teaching",
        default_domain="cell_biology",
        application_template="Apply {name} while teaching {primary} from the verified lesson.",
    )


def assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    objectives = []
    try:
        learn = dict(uli.learning_structure())
        objectives = list(learn.get("learning_objectives") or [])
    except Exception:  # noqa: BLE001
        objectives = []
    practices = (
        "asking_questions",
        "developing_models",
        "planning_investigations",
        "analysing_data",
        "constructing_explanations",
        "laboratory_skills",
        "practical_biology",
    )
    hints = []
    for i, obj in enumerate(objectives[:8]):
        text = obj.get("objective") if isinstance(obj, Mapping) else str(obj)
        hints.append(
            {
                "objective_ref": text,
                "bloom_hint": "apply" if i % 2 == 0 else "understand",
                "dok_hint": "2" if i < 4 else "3",
                "scientific_practice": practices[i % len(practices)],
                "practical_competency": "laboratory"
                if (domains and domains[0]["domain"] == "laboratory")
                else "conceptual",
                "cognitive_demand": "medium",
                "difficulty_estimate": "developing",
                "diagnostic_focus": domains[0]["domain"] if domains else "general",
                "owner": "AME",
                "provenance": "biology_intelligence.assessment",
            }
        )
    if not hints:
        hints.append(
            {
                "objective_ref": None,
                "bloom_hint": "understand",
                "dok_hint": "2",
                "scientific_practice": "developing_models",
                "practical_competency": "conceptual",
                "cognitive_demand": "medium",
                "difficulty_estimate": "developing",
                "diagnostic_focus": domains[0]["domain"] if domains else "general",
                "owner": "AME",
                "provenance": "biology_intelligence.assessment",
            }
        )
    return hints


def revision_summary(domains: list[dict[str, Any]], misconceptions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "focus_domains": [d["domain"] for d in domains[:4]],
        "retrieval_prompts": [
            "State the key biological principle from today's lesson in one sentence.",
            "Sketch or label the main diagram from memory, then check against the source.",
            "Explain a common misconception and the correct scientific model.",
        ],
        "spaced_practice": {"recommended_intervals_days": [1, 3, 7], "interleave": True},
        "misconception_review_ids": [m.get("misconception_id") for m in misconceptions[:6]],
        "provenance": "biology_intelligence.revision",
    }


def accessibility_guidance(uli: Any) -> list[dict[str, Any]]:
    reading = {}
    try:
        a11y = dict(uli.accessibility_structure())
        reading = dict(a11y.get("reading_level") or {})
    except Exception:  # noqa: BLE001
        reading = {}
    return [
        {
            "recommendation": "simplified_biological_terminology",
            "detail": "Gloss technical terms (mitosis, osmosis, phenotype) beside first use.",
            "owner": "AIE",
        },
        {
            "recommendation": "diagram_descriptions",
            "detail": "Provide structured alt text / descriptions for labelled biological diagrams.",
            "owner": "AIE/VMLE",
        },
        {
            "recommendation": "stepwise_process_explanations",
            "detail": "Chunk pathways (e.g. photosynthesis stages) into ordered steps.",
            "owner": "AIE",
        },
        {
            "recommendation": "alternative_visual_representations",
            "detail": "Offer simplified diagram, full labelled figure, and verbal summary.",
            "owner": "AIE",
        },
        {
            "recommendation": "read_aloud_scientific_terminology",
            "detail": "TTS-friendly pronunciations for taxa, organelle, and gene names.",
            "owner": "VMLE/AIE",
        },
        {
            "recommendation": "accessible_laboratory_instructions",
            "detail": "Numbered, short lab steps with safety callouts; avoid dense paragraph procedures.",
            "owner": "AIE",
        },
        {
            "recommendation": "cognitive_load_reduction",
            "detail": "Show one organisational level or process stage at a time before combining.",
            "owner": "AIE",
            "reading_band": reading.get("band"),
        },
    ]


def tutor_guidance(misconceptions: list[dict[str, Any]], scaffolds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "mode": "socratic",
            "prompts": [
                "What is the living system or process being described?",
                "Which structures are involved, and what is each one's function?",
                "What evidence from the lesson supports your claim?",
            ],
            "owner": "ATIE",
        },
        {
            "mode": "guided_biological_reasoning",
            "prompts": [
                "Move from structure → function → system effect.",
                "Trace cause and effect through the pathway step by step.",
            ],
            "owner": "ATIE",
        },
        {
            "mode": "scientific_inquiry",
            "prompts": [
                "What would you predict, observe, and how would you explain it (POE)?",
                "How does this fit a claim–evidence–reasoning explanation?",
            ],
            "owner": "ATIE",
        },
        {
            "mode": "laboratory_reasoning",
            "prompts": [
                "Which variables matter in this investigation?",
                "What observations would support or challenge the lesson model?",
            ],
            "owner": "ATIE",
        },
        {
            "mode": "worked_example_fading",
            "scaffold_ids": [s.get("example_id") for s in scaffolds[:3]],
            "owner": "ATIE",
        },
        {
            "mode": "error_diagnosis",
            "misconception_ids": [m.get("misconception_id") for m in misconceptions[:5]],
            "owner": "ATIE",
        },
        {
            "mode": "reflection",
            "prompts": [
                "Which organisational level was easiest to confuse?",
                "How did the diagram change your explanation?",
            ],
            "owner": "ATIE",
        },
    ]


def lxp_interaction_hints(
    visuals: list[dict[str, Any]],
    processes: dict[str, Any],
    labs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    types = {v.get("visual_type") for v in visuals}
    return [
        {"hook_id": "interactive_cell_models", "available": "interactive_cell_model" in types or "cell_diagram" in types},
        {"hook_id": "human_anatomy_viewers", "available": "human_anatomy_viewer" in types},
        {"hook_id": "plant_anatomy_viewers", "available": "plant_anatomy_viewer" in types},
        {"hook_id": "life_cycle_animations", "available": "life_cycle_animation" in types},
        {"hook_id": "food_web_exploration", "available": "food_web" in types or "food_chain" in types},
        {"hook_id": "dna_visualization", "available": "dna_visualization" in types or "dna_structure" in types},
        {"hook_id": "ecological_simulations", "available": "ecological_simulation" in types},
        {"hook_id": "interactive_lab_activities", "available": bool(labs) or "interactive_lab" in types},
        {"hook_id": "process_count", "count": len(processes.get("processes") or [])},
        *[
            {"hook_id": "recommended_visual", "visual_type": v.get("visual_type"), "label": v.get("label")}
            for v in visuals[:6]
        ],
    ]
