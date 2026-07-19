"""CEF search — board/subject/grade/competency/topic + UCF index."""

from __future__ import annotations

from typing import Any

from engines.curriculum_expansion_framework.localization import normalize_search_term
from engines.curriculum_expansion_framework.registry import list_curricula
from engines.universal_curriculum_framework.search import search_curriculum


def search_expansion(
    query: str,
    *,
    board: str = "",
    subject: str = "",
    grade: str = "",
    competency: str = "",
    limit: int = 25,
    locale: str = "en-IN",
) -> dict[str, Any]:
    q = normalize_search_term(query, locale)
    hits: list[dict[str, Any]] = []

    # Registry metadata hits
    for row in list_curricula():
        blob = " ".join(
            str(x)
            for x in [
                row.get("curriculum_id"),
                row.get("board_name"),
                row.get("programme"),
                " ".join(row.get("subjects") or []),
                " ".join(row.get("grade_levels") or []),
            ]
        ).lower()
        if q and q not in blob and query.lower() not in blob:
            continue
        if board and board.lower() not in (row.get("curriculum_id") or "", row.get("ucf_board_id") or ""):
            continue
        hits.append({"type": "registry", "curriculum": row, "score": 1.0})

    # UCF content search
    ucf = search_curriculum(query or q, board_id=board, limit=limit)
    for h in ucf.get("hits") or []:
        if subject and subject.lower() not in str(h.get("subject") or "").lower():
            continue
        if grade and grade.lower() not in str(h.get("grade") or "").lower():
            continue
        if competency and competency.lower() not in str(h).lower():
            continue
        hits.append({"type": "ucf", **h})

    return {
        "ok": True,
        "query": query,
        "normalized": q,
        "hits": hits[:limit],
        "facets": {"board": board, "subject": subject, "grade": grade, "competency": competency},
        "source": ["cef_registry", "ucf_search"],
    }
