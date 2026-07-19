"""Prerequisite graph utilities over UCF packages."""

from __future__ import annotations

from typing import Any


def build_dependency_graph(package: dict[str, Any]) -> dict[str, Any]:
    nodes = []
    edges = []
    for t in package.get("topics") or []:
        tid = t.get("topic_id")
        nodes.append({"id": tid, "title": t.get("title")})
        pr = t.get("prerequisites") or {}
        for e in pr.get("edges") or []:
            edges.append(
                {
                    "from": e.get("from") or e.get("from_concept"),
                    "to": e.get("to") or e.get("to_concept") or tid,
                    "relation": e.get("relation") or "requires",
                }
            )
        for prev in pr.get("previous_concepts") or []:
            edges.append({"from": prev, "to": tid, "relation": "requires"})
    # dedupe edges
    seen = set()
    uniq = []
    for e in edges:
        key = (e.get("from"), e.get("to"), e.get("relation"))
        if key in seen or not e.get("from"):
            continue
        seen.add(key)
        uniq.append(e)
    return {"nodes": nodes, "edges": uniq, "knowledge_graph": True}


def previous_current_future(topic: dict[str, Any]) -> dict[str, Any]:
    pr = topic.get("prerequisites") or {}
    return {
        "previous": pr.get("previous_concepts") or [],
        "current": pr.get("current_concepts") or [topic.get("topic_id")],
        "future": pr.get("future_concepts") or [],
        "cross_disciplinary": pr.get("cross_disciplinary_links") or [],
    }
