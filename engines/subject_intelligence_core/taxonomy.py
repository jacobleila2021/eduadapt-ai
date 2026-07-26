"""Domain / prerequisite / concept-graph helpers (taxonomy of subject domains)."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from engines.subject_intelligence_core.utilities import learning_structure_dict


def detect_domains(
    text: str,
    domain_markers: Mapping[str, Sequence[str]],
) -> list[dict[str, Any]]:
    blob = (text or "").lower()
    found: list[dict[str, Any]] = []
    for domain, markers in domain_markers.items():
        hits = [m for m in markers if m in blob]
        if hits:
            found.append({"domain": domain, "markers": hits[:6], "score": len(hits)})
    found.sort(key=lambda r: r["score"], reverse=True)
    return found


def prerequisite_hints(
    domains: list[dict[str, Any]],
    edges: Sequence[tuple[str, str]],
    *,
    provenance: str,
) -> dict[str, Any]:
    active = {d["domain"] for d in domains}
    required: list[dict[str, str]] = []
    for pre, post in edges:
        if post in active:
            required.append(
                {
                    "prerequisite": pre,
                    "for_domain": post,
                    "rationale": f"{pre} concepts typically underpin {post} instruction.",
                }
            )
    return {
        "active_domains": sorted(active),
        "edges": required,
        "provenance": provenance,
    }


def concept_graph_from_uli(
    uli: Any,
    domains: list[dict[str, Any]],
    edges: Sequence[tuple[str, str]],
    *,
    domain_node_type: str,
    provenance: str,
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    out_edges: list[dict[str, Any]] = []
    learn = learning_structure_dict(uli)
    for c in learn.get("key_concepts") or []:
        if isinstance(c, dict):
            cid = str(c.get("concept") or "")
            if cid:
                nodes.append(
                    {
                        "id": cid,
                        "type": "uli_concept",
                        "source_refs": c.get("source_refs") or [],
                    }
                )
    for d in domains:
        nodes.append({"id": d["domain"], "type": domain_node_type, "score": d["score"]})
    for pre, post in edges:
        if any(n["id"] == post for n in nodes) or any(n["id"] == pre for n in nodes):
            out_edges.append({"from": pre, "to": post, "relation": "prerequisite"})
    return {"nodes": nodes, "edges": out_edges, "provenance": provenance}
