"""Physics visual / diagram recommendations (metadata only; LXP/VMLE render)."""

from __future__ import annotations

from typing import Any

from engines.physics_intelligence.domains import detect_domains

VISUAL_CATALOGUE: dict[str, list[dict[str, str]]] = {
    "forces": [
        {"visual_type": "force_diagram", "label": "Free-body / force diagram"},
        {"visual_type": "vector_diagram", "label": "Vector diagram"},
    ],
    "motion": [
        {"visual_type": "motion_graph", "label": "Motion graph (s–t / v–t / a–t)"},
        {"visual_type": "interactive_graph", "label": "Interactive kinematics graph"},
    ],
    "mechanics": [
        {"visual_type": "force_diagram", "label": "Mechanics force diagram"},
        {"visual_type": "vector_diagram", "label": "Resultant vector diagram"},
    ],
    "energy": [
        {"visual_type": "energy_flow_diagram", "label": "Energy flow diagram"},
    ],
    "momentum": [
        {"visual_type": "vector_diagram", "label": "Momentum vector diagram"},
        {"visual_type": "interactive_simulation", "label": "Collision simulation"},
    ],
    "electricity": [
        {"visual_type": "circuit_diagram", "label": "Circuit diagram"},
        {"visual_type": "circuit_builder", "label": "Circuit builder"},
    ],
    "magnetism": [
        {"visual_type": "field_diagram", "label": "Magnetic field diagram"},
    ],
    "optics": [
        {"visual_type": "ray_diagram", "label": "Ray diagram"},
        {"visual_type": "ray_tracing", "label": "Ray tracing"},
    ],
    "waves": [
        {"visual_type": "wave_diagram", "label": "Wave diagram"},
        {"visual_type": "wave_animation", "label": "Wave animation"},
    ],
    "thermodynamics": [
        {"visual_type": "energy_flow_diagram", "label": "Heat transfer diagram"},
        {"visual_type": "experimental_apparatus", "label": "Thermal apparatus"},
    ],
    "measurements": [
        {"visual_type": "experimental_apparatus", "label": "Measuring instruments"},
        {"visual_type": "interactive_graph", "label": "Data graph"},
    ],
}

REPRESENTATION_MODES = (
    {"mode": "concrete", "framework": "CRA", "description": "Apparatus / physical demo"},
    {"mode": "representational", "framework": "CRA", "description": "Diagrams, graphs, simulations"},
    {"mode": "abstract", "framework": "CRA", "description": "Formulae and symbolic models"},
    {"mode": "experimental", "framework": "inquiry", "description": "Predict–observe–explain cycles"},
)


def recommend_visuals_for_text(text: str, *, limit: int = 10) -> list[dict[str, Any]]:
    from engines.subject_intelligence_core.diagrams import recommend_visuals_from_catalogue

    domains = detect_domains(text)
    return recommend_visuals_from_catalogue(
        domains,
        VISUAL_CATALOGUE,
        provenance="physics_intelligence.visualizations",
        limit=limit,
        default_visual={"visual_type": "concept_map", "label": "Physics concept map"},
    )


def representation_plan(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "frameworks": ["inquiry", "poe", "cer", "CRA", "guided_discovery"],
        "modes": list(REPRESENTATION_MODES),
        "suggested_sequence": ["concrete", "representational", "abstract"],
        "active_domains": [d["domain"] for d in domains],
        "provenance": "physics_intelligence.diagrams",
    }
