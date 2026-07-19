"""REST-shaped API facade for Curriculum Intelligence Engine."""

from __future__ import annotations

from typing import Any

from engines.curriculum_intelligence_engine import concepts as concept_mod
from engines.curriculum_intelligence_engine import mapping as map_mod
from engines.curriculum_intelligence_engine import model as model_mod
from engines.curriculum_intelligence_engine import prerequisites as prereq_mod
from engines.curriculum_intelligence_engine import progression as prog_mod
from engines.curriculum_intelligence_engine.intelligence import (
    analyze_lesson_context,
    compare_boards,
    ensure_indexed,
    get_runtime,
    outcome_coverage_report,
    search,
)


def api_list_curricula() -> dict[str, Any]:
    return {"curricula": model_mod.supported_curricula(), "active": get_runtime()["ref"].to_dict()}


def api_retrieve_curriculum(curriculum_id: str | None = None) -> dict[str, Any]:
    rt = get_runtime()
    ref = rt["ref"].to_dict()
    if curriculum_id and curriculum_id != ref.get("curriculum_id"):
        return {"ok": False, "error": f"Unknown curriculum_id (pilot only): {curriculum_id}", "active": ref}
    return {
        "ok": True,
        "curriculum": ref,
        "graph_stats": {
            "concepts": len(rt["graph"].concepts),
            "outcomes": len(rt["graph"].outcomes),
            "competencies": len(rt["competencies"]),
        },
        "edition": (rt["data"].get("edition") or ""),
        "version": rt["data"].get("version"),
    }


def api_retrieve_subject(subject: str, grade: str | None = None) -> dict[str, Any]:
    rt = get_runtime()
    rows = concept_mod.list_concepts(rt["graph"], subject=subject, grade=grade)
    return {"subject": subject, "grade": grade, "concepts": rows, "count": len(rows)}


def api_retrieve_chapter(chapter: int) -> dict[str, Any]:
    rt = get_runtime()
    rows = concept_mod.list_concepts(rt["graph"], chapter=chapter)
    title = rows[0].get("chapter_title") if rows else ""
    return {"chapter": chapter, "chapter_title": title, "concepts": rows, "count": len(rows)}


def api_retrieve_concept(concept_id: str) -> dict[str, Any]:
    rt = get_runtime()
    row = concept_mod.get_concept(rt["graph"], concept_id)
    if not row:
        return {"ok": False, "error": "concept not found"}
    return {"ok": True, "concept": row}


def api_retrieve_prerequisite_map(concept_id: str) -> dict[str, Any]:
    rt = get_runtime()
    return prereq_mod.prerequisite_map(rt["graph"], concept_id)


def api_retrieve_competency(competency_id: str) -> dict[str, Any]:
    rt = get_runtime()
    for c in rt["competencies"]:
        if c.competency_id == competency_id:
            return {"ok": True, "competency": c.to_dict()}
    return {"ok": False, "error": "competency not found"}


def api_retrieve_learning_outcomes(concept_id: str | None = None, chapter: int | None = None) -> dict[str, Any]:
    rt = get_runtime()
    rows = [o.to_dict() for o in rt["graph"].outcomes.values()]
    if concept_id:
        rows = [o for o in rows if concept_id in (o.get("concept_ids") or [])]
    if chapter is not None:
        rows = [o for o in rows if o.get("chapter") == chapter]
    return {"outcomes": rows, "count": len(rows)}


def api_compare_curricula(board_a: str, board_b: str) -> dict[str, Any]:
    return compare_boards(board_a, board_b)


def api_search_concepts(query: str, limit: int = 20) -> dict[str, Any]:
    rt = get_runtime()
    return {"results": concept_mod.search_concepts(rt["graph"], query, limit=limit)}


def api_search_competencies(query: str) -> dict[str, Any]:
    rt = get_runtime()
    q = (query or "").lower()
    rows = [
        c.to_dict()
        for c in rt["competencies"]
        if q in c.name.lower() or q in c.description.lower()
    ]
    return {"results": rows, "count": len(rows)}


def api_search_curriculum_graph(query: str, limit: int = 10) -> dict[str, Any]:
    return search(query, limit=limit)


def api_analyze_lesson(**kwargs: Any) -> dict[str, Any]:
    return analyze_lesson_context(**kwargs)


def api_detect_gaps(concept_id: str, mastered: list[str] | None = None) -> dict[str, Any]:
    rt = get_runtime()
    return prereq_mod.detect_gaps(rt["graph"], concept_id, mastered=mastered)


def api_progression(concept_id: str, current_level: str = "beginning") -> dict[str, Any]:
    rt = get_runtime()
    return prog_mod.progression_for_concept(rt["graph"], concept_id, current_level)


def api_rebuild_index() -> dict[str, Any]:
    return ensure_indexed(force=True)


def api_outcome_coverage(concept_ids: list[str] | None = None) -> dict[str, Any]:
    return outcome_coverage_report(concept_ids)


def api_equivalent_topics(concept_id: str) -> dict[str, Any]:
    rt = get_runtime()
    return {"equivalents": map_mod.equivalent_topics(rt["graph"], concept_id)}
