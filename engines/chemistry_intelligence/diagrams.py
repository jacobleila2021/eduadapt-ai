"""Chemistry visual / diagram recommendations (metadata only)."""

from __future__ import annotations

from typing import Any

from engines.chemistry_intelligence.domains import detect_domains

VISUAL_CATALOGUE: dict[str, list[dict[str, str]]] = {
    "atomic_structure": [
        {"visual_type": "electron_shell_diagram", "label": "Electron shell diagram"},
        {"visual_type": "orbital_diagram", "label": "Orbital diagram"},
    ],
    "periodic_table": [
        {"visual_type": "interactive_periodic_table", "label": "Interactive periodic table"},
    ],
    "chemical_bonding": [
        {"visual_type": "lewis_structure", "label": "Lewis structure"},
        {"visual_type": "electron_dot_diagram", "label": "Electron-dot diagram"},
        {"visual_type": "molecular_geometry", "label": "Molecular geometry model"},
    ],
    "reactions": [
        {"visual_type": "reaction_animation", "label": "Reaction animation"},
        {"visual_type": "equation_balancer_ui", "label": "Interactive balancing exercise"},
    ],
    "stoichiometry": [
        {"visual_type": "stoichiometry_visualization", "label": "Stoichiometry visualization"},
        {"visual_type": "mole_concept_diagram", "label": "Mole concept diagram"},
    ],
    "acids_bases": [
        {"visual_type": "ph_scale", "label": "pH scale"},
        {"visual_type": "titration_curve", "label": "Titration curve"},
    ],
    "organic": [
        {"visual_type": "structural_formula", "label": "Structural formula"},
        {"visual_type": "molecular_viewer_3d", "label": "3D molecule viewer"},
        {"visual_type": "functional_group_map", "label": "Functional group map"},
    ],
    "inorganic": [
        {"visual_type": "crystal_structure", "label": "Crystal structure"},
    ],
    "electrochemistry": [
        {"visual_type": "electrochemical_cell", "label": "Electrochemical cell diagram"},
        {"visual_type": "half_equation_board", "label": "Half-equation board"},
    ],
    "thermochemistry": [
        {"visual_type": "energy_profile", "label": "Energy profile diagram"},
    ],
    "kinetics": [
        {"visual_type": "energy_profile", "label": "Activation energy profile"},
        {"visual_type": "rate_graph", "label": "Rate graph"},
    ],
    "equilibrium": [
        {"visual_type": "equilibrium_shift_diagram", "label": "Equilibrium shift diagram"},
    ],
    "laboratory": [
        {"visual_type": "laboratory_simulation", "label": "Laboratory simulation"},
        {"visual_type": "apparatus_diagram", "label": "Apparatus diagram"},
    ],
}


def recommend_visuals_for_text(text: str, *, limit: int = 10) -> list[dict[str, Any]]:
    from engines.subject_intelligence_core.diagrams import recommend_visuals_from_catalogue

    domains = detect_domains(text)
    return recommend_visuals_from_catalogue(
        domains,
        VISUAL_CATALOGUE,
        provenance="chemistry_intelligence.diagrams",
        limit=limit,
        default_visual={"visual_type": "concept_map", "label": "Chemistry concept map"},
    )


def representation_plan(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "frameworks": ["inquiry", "poe", "cer", "CRA", "guided_discovery", "conceptual_change"],
        "suggested_sequence": ["concrete", "representational", "abstract"],
        "active_domains": [d["domain"] for d in domains],
        "provenance": "chemistry_intelligence.diagrams",
    }
