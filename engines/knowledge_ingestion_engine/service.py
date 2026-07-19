"""Service / API surface for Knowledge Ingestion Engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engines.knowledge_ingestion_engine.pipeline import KnowledgeIngestionPipeline, PACKAGE_DIR

_pipeline: KnowledgeIngestionPipeline | None = None


def get_pipeline() -> KnowledgeIngestionPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = KnowledgeIngestionPipeline()
    return _pipeline


# --- REST-shaped functions (wire to FastAPI/Flask later without changing contracts) ---

def api_upload_document(path: str, **meta: Any) -> dict[str, Any]:
    """POST /kie/documents"""
    return get_pipeline().ingest(path, **meta)


def api_reprocess_document(package_id: str, **meta: Any) -> dict[str, Any]:
    """POST /kie/documents/{id}/reprocess"""
    return get_pipeline().reprocess(package_id, **meta)


def api_retrieve_package(package_id: str) -> dict[str, Any]:
    """GET /kie/packages/{id}"""
    path = PACKAGE_DIR / f"{package_id}.json"
    if not path.is_file():
        return {"ok": False, "error": "not found"}
    import json

    return {"ok": True, "package": json.loads(path.read_text(encoding="utf-8"))}


def api_search_concepts(q: str, k: int = 5) -> dict[str, Any]:
    """GET /kie/search/concepts"""
    return {"ok": True, "results": get_pipeline().search_concepts(q, k)}


def api_search_figures(q: str, k: int = 5) -> dict[str, Any]:
    """GET /kie/search/figures"""
    return {"ok": True, "results": get_pipeline().search_figures(q, k)}


def api_search_formulae(q: str, k: int = 5) -> dict[str, Any]:
    """GET /kie/search/formulae"""
    return {"ok": True, "results": get_pipeline().search_formulae(q, k)}


def api_search_questions(q: str, k: int = 5) -> dict[str, Any]:
    """GET /kie/search/questions"""
    return {"ok": True, "results": get_pipeline().search_questions(q, k)}


def api_rebuild_index(package_id: str) -> dict[str, Any]:
    """POST /kie/packages/{id}/reindex"""
    from engines.knowledge_ingestion_engine.stages.indexing import index_knowledge_package
    import json

    path = PACKAGE_DIR / f"{package_id}.json"
    if not path.is_file():
        return {"ok": False, "error": "not found"}
    data = json.loads(path.read_text(encoding="utf-8"))
    status = index_knowledge_package(data)
    data["index_status"] = status
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return {"ok": True, "index_status": status}


def api_list_packages(limit: int = 50) -> dict[str, Any]:
    """GET /kie/packages"""
    if not PACKAGE_DIR.is_dir():
        return {"ok": True, "packages": []}
    rows = sorted(PACKAGE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return {"ok": True, "packages": [p.stem for p in rows[:limit]]}
