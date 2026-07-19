"""Interactive STEM visuals — wraps verified engines/router; never invents results."""

from __future__ import annotations

from typing import Any


def interactive_bundle(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    outputs = context.get("engine_outputs") or {}
    sa = (outputs.get("scientific_accuracy") or {}).get("payload") or {}
    artifacts = list(sa.get("artifacts") or sa.get("stem", {}).get("artifacts") or [])
    return {
        "policy": "deterministic_engines_only",
        "zoom_pan": True,
        "hotspots": True,
        "labels": True,
        "animations": "when_engine_provides",
        "layer_visibility": True,
        "guided_exploration": True,
        "verified_artifacts": artifacts[:20],
        "math": interactive_math(context),
        "chemistry": interactive_chemistry(context),
        "physics": interactive_physics(context),
        "diagrams": interactive_diagrams(context),
    }


def interactive_math(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    outputs = context.get("engine_outputs") or {}
    sa = (outputs.get("scientific_accuracy") or {}).get("payload") or {}
    artifacts = [
        a for a in (sa.get("artifacts") or [])
        if isinstance(a, dict) and ("math" in str(a.get("kind") or "").lower() or "graph" in str(a.get("kind") or "").lower())
    ]
    return {
        "capabilities": [
            "interactive_graphs",
            "function_sliders",
            "geometry_constructions",
            "equation_solving",
            "step_by_step",
            "coordinate_system",
        ],
        "engine_refs": ["engines.graphs", "engines.geometry.geogebra", "engines.mathematics", "engines.router"],
        "payloads": artifacts[:10],
        "deterministic": True,
    }


def interactive_chemistry(context: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "capabilities": [
            "molecule_rotation",
            "reaction_animation",
            "formula_rendering",
            "equation_balancing_visualization",
            "functional_group_exploration",
            "periodic_table",
        ],
        "engine_refs": ["engines.chemistry.balancer", "engines.chemistry.render"],
        "policy": "never_replace_deterministic_chemistry",
        "deterministic": True,
    }


def interactive_physics(context: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "capabilities": [
            "force_diagrams",
            "circuit_simulations",
            "motion_animations",
            "ray_diagrams",
            "projectile_motion",
            "vector_visualization",
        ],
        "engine_refs": ["engines.physics", "engines.circuits.schemdraw_circuit"],
        "deterministic": True,
    }


def interactive_diagrams(context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Dynamic visual explanations from verified lesson content only."""
    context = context or {}
    topic = (context.get("topic") or context.get("lesson_text") or "").lower()
    themes = []
    for name, keys in (
        ("life_cycles", ("life cycle", "metamorphosis")),
        ("water_cycle", ("water cycle", "evaporation")),
        ("cell_structure", ("cell", "chloroplast", "nucleus")),
        ("fractions", ("fraction",)),
        ("algebra", ("algebra", "equation")),
        ("electricity", ("circuit", "current", "electric")),
        ("ecosystems", ("ecosystem", "food chain")),
    ):
        if any(k in topic for k in keys):
            themes.append(name)
    return {
        "themes": themes,
        "source": "verified_lesson_content",
        "interaction": ["zoom", "pan", "hotspots", "labels", "layers"],
    }
