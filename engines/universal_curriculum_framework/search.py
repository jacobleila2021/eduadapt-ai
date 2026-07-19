"""Deterministic search over UCF packages (Chroma optional enrichment)."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework.curriculum_registry import list_packages, load_package


def search_curriculum(query: str, *, board_id: str = "", limit: int = 20) -> dict[str, Any]:
    q = (query or "").lower().strip()
    hits: list[dict[str, Any]] = []
    for meta in list_packages(board_id=board_id, status="active"):
        doc = load_package(meta["package_id"])
        if not doc:
            continue
        for t in doc.get("topics") or []:
            blob = " ".join(
                [
                    str(t.get("title") or ""),
                    str(t.get("topic_id") or ""),
                    " ".join((t.get("objectives") or {}).get("knowledge") or []),
                    " ".join(c.get("description") or "" for c in (t.get("competencies") or []) if isinstance(c, dict)),
                ]
            ).lower()
            if not q or q in blob:
                hits.append(
                    {
                        "package_id": doc.get("package_id"),
                        "topic_id": t.get("topic_id"),
                        "title": t.get("title"),
                        "board": (doc.get("board") or {}).get("board_id"),
                        "score": 1.0 if q and q in str(t.get("title") or "").lower() else 0.6,
                    }
                )
        if len(hits) >= limit:
            break
    hits = sorted(hits, key=lambda h: h["score"], reverse=True)[:limit]
    return {"ok": True, "query": query, "hits": hits, "retrieval": "deterministic_ucf_index", "chroma_optional": True}
