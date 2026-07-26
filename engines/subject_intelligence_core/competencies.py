"""Competency graph helpers — UCF remains curriculum competency authority."""

from __future__ import annotations

from typing import Any, Sequence


def competency_graph(
    nodes: Sequence[dict[str, Any]],
    edges: Sequence[dict[str, Any]],
    *,
    provenance: str,
) -> dict[str, Any]:
    return {
        "nodes": list(nodes),
        "edges": list(edges),
        "progression": {
            "model": "prerequisite",
            "mastery_owner": "AME",
            "evidence_owner": "AME/LAIE",
        },
        "provenance": provenance,
    }


def from_domain_prereqs(
    domains: list[dict[str, Any]],
    prereq: dict[str, Any],
    *,
    provenance: str,
) -> dict[str, Any]:
    nodes = [{"id": d["domain"], "type": "domain", "score": d.get("score", 0)} for d in domains]
    edges = [
        {
            "from": e.get("prerequisite"),
            "to": e.get("for_domain"),
            "relation": "prerequisite",
        }
        for e in prereq.get("edges") or []
    ]
    return competency_graph(nodes, edges, provenance=provenance)
