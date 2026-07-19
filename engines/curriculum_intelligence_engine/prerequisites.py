"""Prerequisite engine — dependency trees, gaps, remediation."""

from __future__ import annotations

from typing import Any

from engines.curriculum_intelligence_engine.graph import CurriculumKnowledgeGraph


def prerequisite_map(graph: CurriculumKnowledgeGraph, concept_id: str) -> dict[str, Any]:
    chain = graph.prerequisite_chain(concept_id)
    node = graph.get_concept(concept_id)
    return {
        "concept_id": concept_id,
        "title": node.title if node else "",
        "chain": [
            {
                "concept_id": cid,
                "title": (graph.get_concept(cid).title if graph.get_concept(cid) else cid),
            }
            for cid in chain
        ],
        "dependents": [
            {
                "concept_id": cid,
                "title": (graph.get_concept(cid).title if graph.get_concept(cid) else cid),
            }
            for cid in graph.dependents(concept_id)
        ],
    }


def detect_gaps(
    graph: CurriculumKnowledgeGraph,
    target_concept: str,
    mastered: list[str] | None = None,
) -> dict[str, Any]:
    mastered_set = set(mastered or [])
    missing = graph.missing_prerequisites(target_concept, mastered_set)
    remediation = []
    for cid in missing:
        n = graph.get_concept(cid)
        remediation.append(
            {
                "concept_id": cid,
                "title": n.title if n else cid,
                "recommendation": f"Review '{n.title if n else cid}' before advancing.",
                "difficulty": n.difficulty if n else "medium",
            }
        )
    return {
        "target": target_concept,
        "mastered": sorted(mastered_set),
        "missing_prerequisites": missing,
        "has_gaps": bool(missing),
        "remediation": remediation,
    }


def dependency_tree(graph: CurriculumKnowledgeGraph, root_ids: list[str] | None = None) -> dict[str, Any]:
    roots = root_ids or [
        cid
        for cid, node in graph.concepts.items()
        if not graph.prerequisite_chain(cid)
    ]
    trees = []
    for rid in roots:
        trees.append(
            {
                "root": rid,
                "title": graph.get_concept(rid).title if graph.get_concept(rid) else rid,
                "children": _subtree(graph, rid, depth=0, max_depth=4),
            }
        )
    return {"trees": trees, "root_count": len(trees)}


def _subtree(graph: CurriculumKnowledgeGraph, cid: str, depth: int, max_depth: int) -> list[dict[str, Any]]:
    if depth >= max_depth:
        return []
    kids = []
    for child in graph.dependents(cid):
        n = graph.get_concept(child)
        kids.append(
            {
                "concept_id": child,
                "title": n.title if n else child,
                "children": _subtree(graph, child, depth + 1, max_depth),
            }
        )
    return kids
