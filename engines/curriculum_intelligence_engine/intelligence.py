"""Curriculum Intelligence — main facade used by CurriculumEngine / APIs."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from engines.curriculum_intelligence_engine import adaptations as adapt_mod
from engines.curriculum_intelligence_engine import concepts as concept_mod
from engines.curriculum_intelligence_engine import mapping as map_mod
from engines.curriculum_intelligence_engine import model as model_mod
from engines.curriculum_intelligence_engine import outcomes as outcome_mod
from engines.curriculum_intelligence_engine import prerequisites as prereq_mod
from engines.curriculum_intelligence_engine import progression as prog_mod
from engines.curriculum_intelligence_engine import search as search_mod
from engines.curriculum_intelligence_engine.indexing import index_curriculum_graph
from engines.curriculum_intelligence_engine.ontology import (
    curriculum_ref_from_ontology,
    load_default_ontology,
)
from engines.curriculum_intelligence_engine.schemas import Competency


@lru_cache(maxsize=1)
def get_runtime() -> dict[str, Any]:
    data, graph, comps = load_default_ontology()
    return {
        "data": data,
        "graph": graph,
        "competencies": list(comps),
        "ref": curriculum_ref_from_ontology(data),
        "index_status": None,
    }


def ensure_indexed(force: bool = False) -> dict[str, Any]:
    rt = get_runtime()
    if rt["index_status"] and not force:
        return rt["index_status"]
    status = index_curriculum_graph(rt["graph"], rt["competencies"])
    # mutate cached runtime carefully
    get_runtime.cache_clear()
    rt2 = get_runtime()
    # re-index already done; stash on fresh runtime via module-level
    _store_index_status(status)
    return status


_INDEX_STATUS: dict[str, Any] | None = None


def _store_index_status(status: dict[str, Any]) -> None:
    global _INDEX_STATUS
    _INDEX_STATUS = status


def get_index_status() -> dict[str, Any] | None:
    return _INDEX_STATUS


def analyze_lesson_context(
    *,
    lesson_text: str = "",
    topic: str = "",
    board: str | None = None,
    grade: str | None = None,
    subject: str | None = None,
    mastered: list[str] | None = None,
    reindex: bool = False,
) -> dict[str, Any]:
    """
    Produce curriculum intelligence payload for VLIE CurriculumEngine.
    Does not replace knowledge RAG — enriches it.
    """
    rt = get_runtime()
    graph = rt["graph"]
    ref = rt["ref"]
    if reindex:
        ensure_indexed(force=True)

    requested_grade = str(grade or ref.grade).strip().lower()
    requested_subject = str(subject or ref.subject).strip().lower()
    ref_grade = str(ref.grade or "").strip().lower()
    ref_subject = str(ref.subject or "").strip().lower()
    science_subjects = {
        "science",
        "general science",
        "biology",
        "chemistry",
        "physics",
        "earth science",
        "environmental science",
    }
    subject_matches = (
        requested_subject == ref_subject
        or (ref_subject == "science" and requested_subject in science_subjects)
    )
    grade_matches = not requested_grade or not ref_grade or requested_grade == ref_grade
    scope_matched = subject_matches and grade_matches

    matched = (
        concept_mod.match_lesson_concepts(graph, lesson_text, topic=topic)
        if scope_matched
        else []
    )
    primary_id = matched[0]["concept_id"] if matched else None

    prereqs = prereq_mod.prerequisite_map(graph, primary_id) if primary_id else {}
    gaps = (
        prereq_mod.detect_gaps(graph, primary_id, mastered=mastered)
        if primary_id
        else {"has_gaps": False}
    )
    los = [
        o.to_dict()
        for o in graph.outcomes.values()
        if primary_id and primary_id in o.concept_ids
    ]
    comps: list[Competency] = [
        c
        for c in rt["competencies"]
        if primary_id and primary_id in c.related_concepts
    ]
    progression = (
        prog_mod.progression_for_concept(graph, primary_id)
        if primary_id
        else {}
    )
    next_recs = (
        prog_mod.recommend_next(
            graph,
            mastered or [],
            chapter=matched[0].get("chapter") if matched else None,
        )
        if primary_id
        else []
    )
    adaptations = adapt_mod.adaptations_for_concept(primary_id) if primary_id else {}
    cross = graph.cross_links_for(primary_id) if primary_id else []
    path = model_mod.build_unified_path(
        board=board or ref.board,
        programme=ref.programme,
        grade=grade or ref.grade,
        subject=subject or ref.subject,
        chapter=matched[0].get("chapter", 0) if matched else 0,
        chapter_title=matched[0].get("chapter_title", "") if matched else "",
        topic=topic or (matched[0].get("topic") if matched else ""),
        concept=matched[0].get("title") if matched else "",
        learning_objective=los[0]["statement"] if los else "",
    )

    return {
        "curriculum_ref": ref.to_dict(),
        "unified_path": path,
        "matched_concepts": matched,
        "primary_concept_id": primary_id,
        "prerequisites": prereqs,
        "learning_gaps": gaps,
        "learning_outcomes": los,
        "competencies": [c.to_dict() for c in comps],
        "progression": progression,
        "next_concepts": next_recs[:5],
        "cross_curriculum": cross,
        "adaptations": adaptations,
        "supported_curricula": model_mod.supported_curricula(),
        "graph_stats": {
            "concepts": len(graph.concepts),
            "outcomes": len(graph.outcomes),
            "edges": len(graph.prerequisites),
            "cross_links": len(graph.cross_links),
        },
        "index_status": get_index_status(),
        "scope_matched": scope_matched,
        "scope": {
            "requested_grade": grade or ref.grade,
            "requested_subject": subject or ref.subject,
            "ontology_grade": ref.grade,
            "ontology_subject": ref.subject,
        },
        "policy": {
            "does_not_generate_lessons": True,
            "presentation_adaptations_only": True,
            "wraps_knowledge_layer": True,
        },
    }


def compare_boards(board_a: str, board_b: str) -> dict[str, Any]:
    rt = get_runtime()
    return map_mod.compare_curricula(rt["graph"], board_a, board_b)


def search(query: str, limit: int = 10) -> dict[str, Any]:
    rt = get_runtime()
    return search_mod.search_curriculum(rt["graph"], query, limit=limit)


def outcome_coverage_report(concept_ids: list[str] | None = None) -> dict[str, Any]:
    rt = get_runtime()
    ids = concept_ids or list(rt["graph"].concepts.keys())
    outcomes = [o.to_dict() for o in rt["graph"].outcomes.values()]
    return outcome_mod.outcome_coverage(ids, outcomes)
