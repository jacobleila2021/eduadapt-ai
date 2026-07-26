"""Assessment / accessibility / teaching-strategy metadata for CIP."""

from __future__ import annotations

from typing import Any, Mapping

TEACHING_FRAMEWORKS: tuple[dict[str, str], ...] = (
    {"id": "inquiry", "name": "Inquiry-Based Learning"},
    {"id": "poe", "name": "Predict–Observe–Explain"},
    {"id": "cer", "name": "Claim–Evidence–Reasoning"},
    {"id": "cra", "name": "Concrete–Representational–Abstract"},
    {"id": "experimental_investigation", "name": "Experimental Investigation"},
    {"id": "guided_discovery", "name": "Guided Discovery"},
    {"id": "conceptual_change", "name": "Conceptual Change"},
    {"id": "retrieval_practice", "name": "Retrieval Practice"},
)


def teaching_strategies(domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from engines.subject_intelligence_core.pedagogy import build_teaching_strategies

    return build_teaching_strategies(
        TEACHING_FRAMEWORKS,
        domains,
        provenance="chemistry_intelligence.teaching",
        default_domain="reactions",
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
                "practical_competency": "laboratory" if "lab" in (domains[0]["domain"] if domains else "") else "conceptual",
                "cognitive_demand": "medium",
                "difficulty_estimate": "developing",
                "diagnostic_focus": domains[0]["domain"] if domains else "general",
                "owner": "AME",
                "provenance": "chemistry_intelligence.assessment",
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
                "provenance": "chemistry_intelligence.assessment",
            }
        )
    return hints


def revision_summary(domains: list[dict[str, Any]], misconceptions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "focus_domains": [d["domain"] for d in domains[:4]],
        "retrieval_prompts": [
            "State the key chemical principle from today's lesson in one sentence.",
            "Write/interpret one source equation with state symbols if given.",
            "Explain a common misconception and the correct model.",
        ],
        "spaced_practice": {"recommended_intervals_days": [1, 3, 7], "interleave": True},
        "misconception_review_ids": [m.get("misconception_id") for m in misconceptions[:6]],
        "provenance": "chemistry_intelligence.revision",
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
            "recommendation": "simplified_chemistry_language",
            "detail": "Gloss terms (mole, ion, catalyst, equilibrium) beside first use.",
            "owner": "AIE",
        },
        {
            "recommendation": "stepwise_equation_explanations",
            "detail": "Reveal equation transformations one coefficient/step at a time.",
            "owner": "AIE",
        },
        {
            "recommendation": "molecule_descriptions",
            "detail": "Provide structured verbal descriptions of molecular models and formulae.",
            "owner": "AIE/VMLE",
        },
        {
            "recommendation": "diagram_alt_text",
            "detail": "Alt text for Lewis, apparatus, and energy-profile diagrams.",
            "owner": "AIE",
        },
        {
            "recommendation": "read_aloud_notation",
            "detail": "TTS-friendly readings for subscripts, charges, and state symbols.",
            "owner": "VMLE/AIE",
        },
        {
            "recommendation": "alternative_representations",
            "detail": "Offer formula, structural, and particulate models before combining them.",
            "owner": "AIE",
        },
        {
            "recommendation": "cognitive_load_reduction",
            "detail": "Chunk multi-step stoichiometry; show one representation at a time.",
            "owner": "AIE",
            "reading_band": reading.get("band"),
        },
    ]


def tutor_guidance(misconceptions: list[dict[str, Any]], scaffolds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "mode": "socratic",
            "prompts": [
                "What particles are involved, and how are they rearranging?",
                "Which quantities are known (mass, moles, concentration)?",
                "Which lesson principle connects reactants to products?",
            ],
            "owner": "ATIE",
        },
        {
            "mode": "graduated_hints",
            "levels": [
                "Hint 1: Name the topic family (bonding, moles, acid–base, redox).",
                "Hint 2: Point to the relevant equation or mole map without revealing the answer.",
                "Hint 3: Offer a simpler isomorphic numerical case from the same principle.",
            ],
            "owner": "ATIE",
        },
        {
            "mode": "reaction_reasoning",
            "prompts": [
                "What is conserved in this change?",
                "How do state symbols and conditions constrain the model?",
            ],
            "owner": "ATIE",
        },
        {
            "mode": "mole_scaffolding",
            "prompts": [
                "Convert to moles before comparing amounts.",
                "Identify the limiting reagent using mole ratios from the balanced equation (verified).",
            ],
            "owner": "ATIE",
        },
        {
            "mode": "laboratory_reasoning",
            "prompts": [
                "What do you predict, observe, and how does evidence support the claim (POE/CER)?",
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
                "Where might a subscript vs coefficient error occur?",
                "Did mass–mole conversions use the correct molar mass from the lesson?",
            ],
            "owner": "ATIE",
        },
    ]


def lxp_interaction_hints(
    visuals: list[dict[str, Any]],
    molecular: dict[str, Any],
    labs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    types = {v.get("visual_type") for v in visuals}
    return [
        {"hook_id": "interactive_periodic_table", "available": "interactive_periodic_table" in types},
        {"hook_id": "molecular_viewers", "available": bool(molecular.get("representation_hooks"))},
        {"hook_id": "molecule_3d", "available": "molecular_viewer_3d" in types},
        {"hook_id": "reaction_animations", "available": "reaction_animation" in types},
        {"hook_id": "stoichiometry_visualizations", "available": "stoichiometry_visualization" in types},
        {"hook_id": "laboratory_simulations", "available": bool(labs) or "laboratory_simulation" in types},
        {"hook_id": "interactive_balancing", "available": "equation_balancer_ui" in types},
        *[
            {"hook_id": "recommended_visual", "visual_type": v.get("visual_type"), "label": v.get("label")}
            for v in visuals[:6]
        ],
    ]
