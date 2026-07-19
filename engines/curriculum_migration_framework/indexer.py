"""Indexing — searchable metadata + optional UCF/KIE vector hooks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

INDEX_PATH = DATA_DIR / "cmif" / "search_index.json"


def _load() -> dict[str, Any]:
    if not INDEX_PATH.is_file():
        return {"entries": []}
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def _save(data: dict[str, Any]) -> None:
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def index_package(package: dict[str, Any], *, lazy: bool = False) -> dict[str, Any]:
    """Build facet search entry. Lazy mode records stub only."""
    entry = {
        "package_id": package.get("package_id") or package.get("curriculum_id"),
        "board": package.get("board"),
        "subject": package.get("subject"),
        "grade": package.get("grade"),
        "unit": [u.get("title") if isinstance(u, dict) else str(u) for u in (package.get("units") or [])],
        "chapter": [c.get("title") if isinstance(c, dict) else str(c) for c in (package.get("chapters") or [])],
        "topic": [t.get("title") if isinstance(t, dict) else str(t) for t in (package.get("topics") or [])],
        "competency": package.get("competencies") or [],
        "learning_objective": package.get("learning_objectives") or [],
        "bloom": package.get("blooms"),
        "dok": package.get("dok"),
        "formula": [f.get("latex") if isinstance(f, dict) else str(f) for f in (package.get("formulae") or [])],
        "diagram": [d.get("diagram_id") if isinstance(d, dict) else str(d) for d in (package.get("figures") or [])],
        "question": [q.get("question_id") if isinstance(q, dict) else str(q) for q in (package.get("official_questions") or [])],
        "publisher": package.get("publisher"),
        "version": package.get("version"),
        "keyword": " ".join(
            str(x)
            for x in [
                package.get("board"),
                package.get("subject"),
                package.get("grade"),
                *[t.get("title") if isinstance(t, dict) else t for t in (package.get("topics") or [])[:12]],
            ]
            if x
        ).lower(),
        "lazy": lazy,
    }
    data = _load()
    entries = [e for e in data.get("entries") or [] if e.get("package_id") != entry["package_id"]]
    entries.append(entry)
    data["entries"] = entries[-2000:]
    _save(data)

    # Optional UCF index
    vector = {"ok": False, "skipped": True}
    if not lazy and package.get("package_id"):
        try:
            from engines.universal_curriculum_framework.indexing import index_package as ucf_index
            from engines.universal_curriculum_framework.curriculum_registry import load_package

            pkg = load_package(str(package["package_id"]))
            if pkg:
                vector = ucf_index(pkg)
        except Exception as exc:  # noqa: BLE001
            vector = {"ok": False, "error": str(exc)}

    return {"ok": True, "entry": entry, "vector": vector, "index_health": {"entries": len(data["entries"])}}


def search_index(
    query: str = "",
    *,
    board: str = "",
    subject: str = "",
    grade: str = "",
    limit: int = 25,
) -> dict[str, Any]:
    q = (query or "").lower().strip()
    hits = []
    for e in _load().get("entries") or []:
        if board and str(e.get("board") or "").lower() != board.lower():
            continue
        if subject and subject.lower() not in str(e.get("subject") or "").lower():
            continue
        if grade and str(e.get("grade") or "") != str(grade):
            continue
        blob = str(e.get("keyword") or "")
        if q and q not in blob and q not in json.dumps(e).lower():
            continue
        hits.append(e)
    return {"ok": True, "hits": hits[:limit], "count": len(hits)}
