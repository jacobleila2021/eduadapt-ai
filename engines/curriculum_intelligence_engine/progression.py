"""Learning progression engine — beginning → mastered."""

from __future__ import annotations

from typing import Any

from engines.curriculum_intelligence_engine.graph import CurriculumKnowledgeGraph
from engines.curriculum_intelligence_engine.schemas import PROGRESSION_ORDER


def progression_for_concept(
    graph: CurriculumKnowledgeGraph,
    concept_id: str,
    current_level: str = "beginning",
) -> dict[str, Any]:
    node = graph.get_concept(concept_id)
    level = (current_level or "beginning").lower()
    if level not in PROGRESSION_ORDER:
        level = "beginning"
    idx = PROGRESSION_ORDER.index(level)
    next_level = PROGRESSION_ORDER[idx + 1] if idx + 1 < len(PROGRESSION_ORDER) else None
    next_concepts = graph.dependents(concept_id)
    return {
        "concept_id": concept_id,
        "title": node.title if node else concept_id,
        "current_level": level,
        "levels": list(PROGRESSION_ORDER),
        "next_level": next_level,
        "next_concepts": [
            {
                "concept_id": cid,
                "title": graph.get_concept(cid).title if graph.get_concept(cid) else cid,
            }
            for cid in next_concepts
        ],
        "recommend_next": (
            next_concepts[0]
            if level in ("proficient", "advanced", "mastered") and next_concepts
            else concept_id
        ),
        "descriptors": {
            "beginning": "Recalls key terms with support.",
            "developing": "Explains concept with examples.",
            "proficient": "Applies concept independently.",
            "advanced": "Transfers concept across contexts.",
            "mastered": "Teaches / evaluates related ideas.",
        },
    }


def recommend_next(
    graph: CurriculumKnowledgeGraph,
    mastered: list[str],
    *,
    chapter: int | None = None,
) -> list[dict[str, Any]]:
    mastered_set = set(mastered)
    candidates = []
    for cid, node in graph.concepts.items():
        if chapter is not None and node.chapter != chapter:
            continue
        if cid in mastered_set:
            continue
        missing = graph.missing_prerequisites(cid, mastered_set)
        if missing:
            continue
        candidates.append(
            {
                "concept_id": cid,
                "title": node.title,
                "chapter": node.chapter,
                "difficulty": node.difficulty,
                "reason": "Prerequisites satisfied",
            }
        )
    candidates.sort(key=lambda r: (r["chapter"], r["title"]))
    return candidates
