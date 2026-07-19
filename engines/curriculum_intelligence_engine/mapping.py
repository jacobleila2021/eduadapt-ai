"""Cross-curriculum mapping — bidirectional board comparisons."""

from __future__ import annotations

from typing import Any

from engines.curriculum_intelligence_engine.graph import CurriculumKnowledgeGraph


def compare_curricula(
    graph: CurriculumKnowledgeGraph,
    board_a: str,
    board_b: str,
) -> dict[str, Any]:
    """
    Compare two boards using seeded cross_maps.
    Source ontology is treated as board_a baseline (usually CBSE/NCERT pilot).
    """
    a = board_a.strip()
    b = board_b.strip()
    equivalents: list[dict[str, Any]] = []
    advanced: list[dict[str, Any]] = []
    optional: list[dict[str, Any]] = []
    missing_for_b: list[dict[str, Any]] = []

    linked_ids = {c.concept_id for c in graph.cross_links if c.board.lower() == b.lower()}

    for concept_id, node in graph.concepts.items():
        links_b = graph.cross_links_for(concept_id, board=b)
        if links_b:
            for link in links_b:
                row = {
                    "concept_id": concept_id,
                    "title_a": node.title,
                    "board_a": a,
                    "board_b": b,
                    "label_b": link.get("label"),
                    "programme_b": link.get("programme"),
                    "link_type": link.get("link_type"),
                }
                lt = (link.get("link_type") or "equivalent").lower()
                if lt == "advanced":
                    advanced.append(row)
                elif lt == "optional":
                    optional.append(row)
                else:
                    equivalents.append(row)
        else:
            missing_for_b.append(
                {
                    "concept_id": concept_id,
                    "title_a": node.title,
                    "board_a": a,
                    "board_b": b,
                    "note": f"No seeded equivalent on {b}",
                }
            )

    return {
        "board_a": a,
        "board_b": b,
        "equivalent_topics": equivalents,
        "advanced_topics": advanced,
        "optional_topics": optional,
        "missing_topics": missing_for_b,
        "extension_pathways": advanced + optional,
        "coverage": {
            "concepts_in_a": len(graph.concepts),
            "mapped_to_b": len(linked_ids),
            "ratio": (len(linked_ids) / len(graph.concepts)) if graph.concepts else 0.0,
        },
    }


def equivalent_topics(graph: CurriculumKnowledgeGraph, concept_id: str) -> list[dict[str, Any]]:
    node = graph.get_concept(concept_id)
    links = graph.cross_links_for(concept_id)
    return [
        {
            "concept_id": concept_id,
            "source_title": node.title if node else concept_id,
            **link,
        }
        for link in links
    ]
