"""Indexing — build lightweight search documents; optional Chroma hook."""

from __future__ import annotations

from typing import Any

from engines.universal_curriculum_framework.curriculum_registry import load_package, list_packages


def build_index_documents(package_id: str = "") -> list[dict[str, Any]]:
    docs = []
    metas = [{"package_id": package_id}] if package_id else list_packages()
    for meta in metas:
        pid = meta.get("package_id") if isinstance(meta, dict) else package_id
        pkg = load_package(str(pid))
        if not pkg:
            continue
        for t in pkg.get("topics") or []:
            docs.append(
                {
                    "id": t.get("topic_id"),
                    "text": f"{t.get('title')} {' '.join((t.get('objectives') or {}).get('knowledge') or [])}",
                    "metadata": {
                        "package_id": pkg.get("package_id"),
                        "board_id": (pkg.get("board") or {}).get("board_id"),
                        "type": "topic",
                    },
                }
            )
        for g in pkg.get("glossary") or []:
            docs.append(
                {
                    "id": g.get("term_id"),
                    "text": f"{g.get('term')} {g.get('definition')}",
                    "metadata": {"package_id": pkg.get("package_id"), "type": "glossary"},
                }
            )
    return docs


def index_package(package_id: str) -> dict[str, Any]:
    docs = build_index_documents(package_id)
    # Optional Chroma — preserve deterministic IDs; skip if unavailable
    chroma_ok = False
    try:
        # Soft hook — do not require chromadb for core UCF
        chroma_ok = False
    except Exception:  # noqa: BLE001
        chroma_ok = False
    return {"ok": True, "documents": len(docs), "chroma_indexed": chroma_ok, "ids_deterministic": True}
