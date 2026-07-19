"""Concept library — centralized lookup over CIE graph."""

from __future__ import annotations

from typing import Any

from engines.curriculum_intelligence_engine.graph import CurriculumKnowledgeGraph
from engines.curriculum_intelligence_engine.schemas import ConceptNode


def get_concept(graph: CurriculumKnowledgeGraph, concept_id: str) -> dict[str, Any] | None:
    node = graph.get_concept(concept_id)
    if not node:
        return None
    d = node.to_dict()
    d["curriculum_path"] = graph.path_summary(concept_id)
    return d


def list_concepts(
    graph: CurriculumKnowledgeGraph,
    *,
    chapter: int | None = None,
    subject: str | None = None,
    grade: str | None = None,
) -> list[dict[str, Any]]:
    rows: list[ConceptNode] = list(graph.concepts.values())
    if chapter is not None:
        rows = [c for c in rows if c.chapter == chapter]
    if subject:
        rows = [c for c in rows if c.subject.lower() == subject.lower()]
    if grade:
        rows = [c for c in rows if grade in c.grade_range or not c.grade_range]
    return [c.to_dict() for c in sorted(rows, key=lambda x: (x.chapter, x.title))]


def search_concepts(graph: CurriculumKnowledgeGraph, query: str, limit: int = 20) -> list[dict[str, Any]]:
    q = (query or "").strip().lower()
    if not q:
        return []
    scored: list[tuple[int, ConceptNode]] = []
    for node in graph.concepts.values():
        hay = " ".join(
            [
                node.concept_id,
                node.title,
                node.definition,
                node.topic,
                node.chapter_title,
                " ".join(node.keywords),
            ]
        ).lower()
        score = 0
        if q in node.title.lower():
            score += 10
        if q in hay:
            score += 5
        for token in q.split():
            if token in hay:
                score += 2
        if score:
            scored.append((score, node))
    scored.sort(key=lambda t: (-t[0], t[1].title))
    return [n.to_dict() for _, n in scored[:limit]]


def match_lesson_concepts(
    graph: CurriculumKnowledgeGraph,
    lesson_text: str,
    topic: str = "",
    limit: int = 8,
) -> list[dict[str, Any]]:
    blob = f"{topic}\n{lesson_text}".lower()
    hits = []
    for node in graph.concepts.values():
        keys = [node.title.lower(), *[k.lower() for k in node.keywords]]
        if any(k and k in blob for k in keys):
            hits.append(node.to_dict())
    # prefer chapter/topic matches first
    if topic:
        t = topic.lower()
        hits.sort(key=lambda c: (0 if t in (c.get("title") or "").lower() or t in (c.get("topic") or "").lower() else 1))
    return hits[:limit]
