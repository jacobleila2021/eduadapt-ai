"""Assessment / accessibility / teaching-strategy metadata for PIP."""

from __future__ import annotations

from typing import Any, Mapping

TEACHING_FRAMEWORKS: tuple[dict[str, str], ...] = (
    {"id": "inquiry", "name": "Inquiry-Based Learning"},
    {"id": "poe", "name": "Predict–Observe–Explain"},
    {"id": "cer", "name": "Claim–Evidence–Reasoning"},
    {"id": "cra", "name": "Concrete–Representational–Abstract"},
    {"id": "guided_discovery", "name": "Guided Discovery"},
    {"id": "experimental_investigation", "name": "Experimental Investigation"},
    {"id": "conceptual_change", "name": "Conceptual Change"},
    {"id": "retrieval_practice", "name": "Retrieval Practice"},
    {"id": "visual_learning", "name": "Visual Learning"},
)


def teaching_strategies(domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from engines.subject_intelligence_core.pedagogy import build_teaching_strategies

    return build_teaching_strategies(
        TEACHING_FRAMEWORKS,
        domains,
        provenance="physics_intelligence.teaching",
        default_domain="mechanics",
        application_template="Apply {name} while teaching {primary} from the verified lesson.",
    )


def assessment_hints(uli: Any, domains: list[dict[str, Any]]) -> list[dict[str, Any]]:
    objectives = []
    try:
        learn = dict(uli.learning_structure())
        objectives = list(learn.get("learning_objectives") or [])
    except Exception:  # noqa: BLE001
        objectives = []
    hints = []
    practices = ("asking_questions", "developing_models", "planning_investigations", "analysing_data", "constructing_explanations")
    for i, obj in enumerate(objectives[:8]):
        text = obj.get("objective") if isinstance(obj, Mapping) else str(obj)
        hints.append(
            {
                "objective_ref": text,
                "bloom_hint": "apply" if i % 2 == 0 else "understand",
                "dok_hint": "2" if i < 4 else "3",
                "scientific_practice": practices[i % len(practices)],
                "cognitive_demand": "medium",
                "difficulty_estimate": "developing",
                "diagnostic_focus": domains[0]["domain"] if domains else "general",
                "owner": "AME",
                "provenance": "physics_intelligence.assessment",
            }
        )
    if not hints:
        hints.append(
            {
                "objective_ref": None,
                "bloom_hint": "understand",
                "dok_hint": "2",
                "scientific_practice": "developing_models",
                "cognitive_demand": "medium",
                "difficulty_estimate": "developing",
                "diagnostic_focus": domains[0]["domain"] if domains else "general",
                "owner": "AME",
                "provenance": "physics_intelligence.assessment",
            }
        )
    return hints


def revision_summary(domains: list[dict[str, Any]], misconceptions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "focus_domains": [d["domain"] for d in domains[:4]],
        "retrieval_prompts": [
            "State the key physical principle from today's lesson in one sentence.",
            "Sketch the diagram that models the situation (forces, rays, or circuit).",
            "Explain a common misconception and the correct scientific model.",
        ],
        "spaced_practice": {"recommended_intervals_days": [1, 3, 7], "interleave": True},
        "misconception_review_ids": [m.get("misconception_id") for m in misconceptions[:6]],
        "provenance": "physics_intelligence.revision",
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
            "recommendation": "simplified_physics_language",
            "detail": "Prefer plain-language glosses beside technical terms (force, field, potential).",
            "owner": "AIE",
        },
        {
            "recommendation": "diagram_descriptions",
            "detail": "Provide alt-text / structured descriptions for force, ray, and circuit diagrams.",
            "owner": "AIE/VMLE",
        },
        {
            "recommendation": "stepwise_equation_explanations",
            "detail": "Expose one algebraic transformation per step with spoken operator names.",
            "owner": "AIE",
        },
        {
            "recommendation": "read_aloud_scientific_notation",
            "detail": "TTS-friendly readings for units and powers (e.g. m/s² as metres per second squared).",
            "owner": "VMLE/AIE",
        },
        {
            "recommendation": "alternative_representations",
            "detail": "Offer graph, diagram, and verbal forms before combining them.",
            "owner": "AIE",
        },
        {
            "recommendation": "cognitive_load_reduction",
            "detail": "Chunk multi-step solutions; show one diagram type at a time.",
            "owner": "AIE",
            "reading_band": reading.get("band"),
        },
    ]


def tutor_guidance(misconceptions: list[dict[str, Any]], scaffolds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "mode": "socratic",
            "prompts": [
                "What is happening physically in this situation?",
                "Which quantities are known, and which are unknowns?",
                "Which lesson principle connects those quantities?",
            ],
            "owner": "ATIE",
        },
        {
            "mode": "graduated_hints",
            "levels": [
                "Hint 1: Name the model (forces, energy, circuit, waves).",
                "Hint 2: Point to the relevant diagram or variable list without revealing the answer.",
                "Hint 3: Offer a simpler isomorphic numerical case from the same principle.",
            ],
            "owner": "ATIE",
        },
        {
            "mode": "experimental_reasoning",
            "prompts": [
                "What do you predict will happen, and why?",
                "What evidence would support or refute your prediction?",
                "How does the observation map to the scientific claim (CER)?",
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
                "Which modelling step was hardest?",
                "Did units and diagram agree with the final claim?",
            ],
            "owner": "ATIE",
        },
    ]


def lxp_interaction_hints(visuals: list[dict[str, Any]], experiments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    types = {v.get("visual_type") for v in visuals}
    return [
        {"hook_id": "interactive_experiments", "available": bool(experiments)},
        {"hook_id": "motion_simulations", "available": "motion_graph" in types or "interactive_graph" in types},
        {"hook_id": "circuit_builders", "available": "circuit_diagram" in types or "circuit_builder" in types},
        {"hook_id": "wave_animations", "available": "wave_diagram" in types or "wave_animation" in types},
        {"hook_id": "ray_tracing", "available": "ray_diagram" in types or "ray_tracing" in types},
        {"hook_id": "force_vectors", "available": "force_diagram" in types or "vector_diagram" in types},
        {"hook_id": "interactive_graphs", "available": "interactive_graph" in types or "motion_graph" in types},
        *[
            {"hook_id": "recommended_visual", "visual_type": v.get("visual_type"), "label": v.get("label")}
            for v in visuals[:6]
        ],
    ]
