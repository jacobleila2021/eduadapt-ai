"""Multiple representations + recommended verified visual types (metadata only)."""

from __future__ import annotations

from typing import Any

from engines.mathematics_intelligence.domains import detect_domains

VISUAL_CATALOGUE: dict[str, list[dict[str, str]]] = {
    "arithmetic": [
        {"visual_type": "number_line", "label": "Number line"},
        {"visual_type": "bar_model", "label": "Bar model"},
        {"visual_type": "fraction_model", "label": "Fraction model"},
        {"visual_type": "place_value_chart", "label": "Place-value chart"},
    ],
    "algebra": [
        {"visual_type": "algebra_tiles", "label": "Algebra tiles"},
        {"visual_type": "balance_scale", "label": "Equation balance"},
        {"visual_type": "function_plot", "label": "Function plot"},
        {"visual_type": "coordinate_plane", "label": "Coordinate plane"},
    ],
    "geometry": [
        {"visual_type": "geometry_construction", "label": "Geometry construction"},
        {"visual_type": "net_3d", "label": "3D net"},
        {"visual_type": "angle_diagram", "label": "Angle diagram"},
    ],
    "trigonometry": [
        {"visual_type": "unit_circle", "label": "Unit circle"},
        {"visual_type": "right_triangle", "label": "Right triangle"},
    ],
    "calculus": [
        {"visual_type": "function_plot", "label": "Function / derivative plot"},
        {"visual_type": "area_under_curve", "label": "Area under curve"},
    ],
    "statistics": [
        {"visual_type": "histogram", "label": "Histogram"},
        {"visual_type": "box_plot", "label": "Box plot"},
        {"visual_type": "scatter_plot", "label": "Scatter plot"},
    ],
    "probability": [
        {"visual_type": "probability_tree", "label": "Probability tree"},
        {"visual_type": "venn_diagram", "label": "Venn diagram"},
    ],
    "number_systems": [
        {"visual_type": "number_line", "label": "Number line"},
        {"visual_type": "venn_diagram", "label": "Number set Venn diagram"},
    ],
}

REPRESENTATION_MODES = (
    {"mode": "concrete", "framework": "CRA", "description": "Manipulatives / physical or virtual objects"},
    {"mode": "representational", "framework": "CRA", "description": "Diagrams, models, number lines"},
    {"mode": "abstract", "framework": "CRA", "description": "Symbols and formal notation"},
    {"mode": "verbal", "framework": "multiple_representations", "description": "Oral / written explanations"},
    {"mode": "tabular", "framework": "multiple_representations", "description": "Tables of values"},
    {"mode": "graphical", "framework": "multiple_representations", "description": "Graphs and plots"},
)


def recommend_visuals_for_text(text: str, *, limit: int = 8) -> list[dict[str, Any]]:
    from engines.subject_intelligence_core.diagrams import recommend_visuals_from_catalogue

    domains = detect_domains(text)
    return recommend_visuals_from_catalogue(
        domains,
        VISUAL_CATALOGUE,
        provenance="mathematics_intelligence.visualizations",
        limit=limit,
        default_visual={"visual_type": "concept_map", "label": "Concept map"},
    )


def representation_plan(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "frameworks": ["CRA", "multiple_representations", "explicit_instruction"],
        "modes": list(REPRESENTATION_MODES),
        "suggested_sequence": ["concrete", "representational", "abstract"],
        "active_domains": [d["domain"] for d in domains],
        "provenance": "mathematics_intelligence.representations",
    }
