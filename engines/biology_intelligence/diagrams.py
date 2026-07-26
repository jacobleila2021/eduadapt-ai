"""Biology diagram / visualization recommendations (metadata only)."""

from __future__ import annotations

from typing import Any

from engines.biology_intelligence.domains import detect_domains

VISUAL_CATALOGUE: dict[str, list[dict[str, str]]] = {
    "cell_biology": [
        {"visual_type": "cell_diagram", "label": "Cell diagram"},
        {"visual_type": "interactive_cell_model", "label": "Interactive cell model"},
        {"visual_type": "chromosome_diagram", "label": "Chromosome diagram"},
    ],
    "anatomy": [
        {"visual_type": "organ_system_diagram", "label": "Organ system diagram"},
        {"visual_type": "labelled_illustration", "label": "Labelled biological illustration"},
        {"visual_type": "human_anatomy_viewer", "label": "Human anatomy viewer"},
        {"visual_type": "tissue_diagram", "label": "Tissue diagram"},
    ],
    "human_biology": [
        {"visual_type": "organ_system_diagram", "label": "Body system diagram"},
        {"visual_type": "human_anatomy_viewer", "label": "Human anatomy viewer"},
    ],
    "plant_biology": [
        {"visual_type": "plant_structure_diagram", "label": "Plant structure diagram"},
        {"visual_type": "plant_anatomy_viewer", "label": "Plant anatomy viewer"},
        {"visual_type": "life_cycle_animation", "label": "Life cycle animation"},
    ],
    "genetics": [
        {"visual_type": "dna_structure", "label": "DNA structure"},
        {"visual_type": "dna_visualization", "label": "DNA visualization"},
        {"visual_type": "chromosome_diagram", "label": "Chromosomes"},
    ],
    "ecology": [
        {"visual_type": "food_chain", "label": "Food chain"},
        {"visual_type": "food_web", "label": "Food web exploration"},
        {"visual_type": "ecological_pyramid", "label": "Ecological pyramid"},
        {"visual_type": "nutrient_cycle", "label": "Carbon / nitrogen / water cycle"},
        {"visual_type": "ecological_simulation", "label": "Ecological simulation"},
    ],
    "evolution": [
        {"visual_type": "evolutionary_tree", "label": "Evolutionary relationships"},
    ],
    "physiology": [
        {"visual_type": "process_animation", "label": "Biological process animation"},
    ],
    "taxonomy": [
        {"visual_type": "classification_key", "label": "Classification / taxonomy key"},
    ],
    "microbiology": [
        {"visual_type": "microscopy_view", "label": "Microscopy view"},
    ],
    "laboratory": [
        {"visual_type": "interactive_lab", "label": "Interactive lab activity"},
        {"visual_type": "apparatus_diagram", "label": "Apparatus diagram"},
    ],
    "biotechnology": [
        {"visual_type": "process_animation", "label": "Biotech process animation"},
    ],
}


def recommend_visuals_for_text(text: str, *, limit: int = 10) -> list[dict[str, Any]]:
    from engines.subject_intelligence_core.diagrams import recommend_visuals_from_catalogue

    domains = detect_domains(text)
    return recommend_visuals_from_catalogue(
        domains,
        VISUAL_CATALOGUE,
        provenance="biology_intelligence.diagrams",
        limit=limit,
        default_visual={"visual_type": "concept_map", "label": "Biology concept map"},
    )


def representation_plan(domains: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "frameworks": [
            "inquiry",
            "poe",
            "cer",
            "concept_mapping",
            "systems_thinking",
            "structure_function",
            "cause_effect",
            "scientific_investigation",
            "retrieval_practice",
        ],
        "suggested_sequence": ["concrete", "diagrammatic", "systems", "abstract"],
        "active_domains": [d["domain"] for d in domains],
        "provenance": "biology_intelligence.diagrams",
    }


def diagram_completeness_signals(visuals: list[dict[str, Any]], domains: list[dict[str, Any]]) -> dict[str, Any]:
    if not domains:
        return {"applicable": False, "completeness": "n/a"}
    return {
        "applicable": True,
        "recommended_count": len(visuals),
        "completeness": "ok" if visuals else "missing",
        "provenance": "biology_intelligence.diagrams",
    }
