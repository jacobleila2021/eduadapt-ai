"""Curriculum search — parse natural queries into CIE hits."""

from __future__ import annotations

import re
from typing import Any

from engines.curriculum_intelligence_engine.concepts import search_concepts
from engines.curriculum_intelligence_engine.graph import CurriculumKnowledgeGraph
from engines.curriculum_intelligence_engine.model import normalize_programme
from engines.knowledge_ingestion_engine.normalization import normalize_board
from engines.curriculum_intelligence_engine.prerequisites import prerequisite_map
from engines.curriculum_intelligence_engine.adaptations import adaptations_for_concept


_BOARD_HINTS = {
    "cbse": "CBSE",
    "ncert": "NCERT",
    "icse": "ICSE",
    "isc": "ISC",
    "cambridge": "Cambridge",
    "igcse": "Cambridge",
    "ib": "IB",
    "myp": "IB",
    "nios": "NIOS",
}


def parse_curriculum_query(query: str) -> dict[str, Any]:
    q = (query or "").strip()
    lower = q.lower()
    board = ""
    for hint, name in _BOARD_HINTS.items():
        if re.search(rf"\b{re.escape(hint)}\b", lower):
            board = name
            break
    grade = ""
    m = re.search(r"(?:class|grade|year)\s*(\d{1,2})", lower)
    if m:
        grade = m.group(1)
    programme = ""
    if "myp" in lower:
        programme = normalize_programme("myp")
    elif "igcse" in lower:
        programme = normalize_programme("igcse")
    return {
        "raw": q,
        "board": normalize_board(board) if board else "",
        "grade": grade,
        "programme": programme,
        "concept_query": q,
    }


def search_curriculum(
    graph: CurriculumKnowledgeGraph,
    query: str,
    *,
    limit: int = 10,
) -> dict[str, Any]:
    parsed = parse_curriculum_query(query)
    concepts = search_concepts(graph, parsed["concept_query"], limit=limit)
    # enrich top hit
    primary = None
    if concepts:
        cid = concepts[0]["concept_id"]
        primary = {
            "concept": concepts[0],
            "curriculum_path": graph.path_summary(cid),
            "prerequisites": prerequisite_map(graph, cid),
            "learning_outcomes": [
                o.to_dict()
                for o in graph.outcomes.values()
                if cid in o.concept_ids
            ],
            "adaptations": adaptations_for_concept(cid),
            "cross_curriculum": graph.cross_links_for(cid),
        }
    return {
        "query": parsed,
        "results": concepts,
        "primary": primary,
        "count": len(concepts),
    }
