"""In-lesson search — lesson, chapter, notes, glossary."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.session_store import search_notes


def search_lesson_text(lesson_text: str, query: str, *, limit: int = 20) -> list[dict[str, Any]]:
    q = (query or "").lower().strip()
    if not q:
        return []
    hits = []
    for i, line in enumerate((lesson_text or "").splitlines()):
        if q in line.lower():
            hits.append({"type": "lesson_line", "line": i + 1, "excerpt": line.strip()[:240]})
            if len(hits) >= limit:
                break
    return hits


def search_all(
    *,
    learner_id: str,
    query: str,
    lesson_text: str = "",
    glossary: list[dict[str, Any]] | None = None,
    scope: str = "all",  # lesson|chapter|subject|notes|glossary|all
) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    if scope in ("all", "lesson", "chapter", "subject"):
        results.extend(search_lesson_text(lesson_text, query))
    if scope in ("all", "notes"):
        for n in search_notes(learner_id, query):
            results.append({"type": "note", **n})
    if scope in ("all", "glossary"):
        q = (query or "").lower()
        for g in glossary or []:
            if q in str(g.get("term") or "").lower() or q in str(g.get("definition") or "").lower():
                results.append({"type": "glossary", **g})
    return {"ok": True, "query": query, "scope": scope, "results": results[:50]}
