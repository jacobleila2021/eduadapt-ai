"""ALE Chroma — pathway/recommendation catalogs (structured state stays in JSON)."""

from __future__ import annotations

from typing import Any

from knowledge.paths import CHROMA_DIR

from engines.adaptive_learning_engine.schemas import DIFFICULTY_LEVELS, PATHWAY_TYPES

ALE_COLLECTIONS = {
    "pathway_types": "ale_pathway_types",
    "difficulty_levels": "ale_difficulty_levels",
    "interventions_index": "ale_interventions_index",
}


def _client():
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def rebuild_ale_index() -> dict[str, Any]:
    status: dict[str, Any] = {"ok": True, "collections": {}}
    try:
        client = _client()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "warning": str(exc), "collections": {}}

    def upsert(name: str, ids: list[str], docs: list[str], metas: list[dict]) -> dict[str, Any]:
        try:
            col = client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
            clean = [
                {k: (v if isinstance(v, (str, int, float, bool)) else str(v)) for k, v in m.items()}
                for m in metas
            ]
            col.upsert(ids=ids, documents=docs, metadatas=clean)
            return {"collection": name, "count": len(ids), "ok": True}
        except Exception as exc:  # noqa: BLE001
            return {"collection": name, "ok": False, "error": str(exc)}

    status["collections"]["pathway_types"] = upsert(
        ALE_COLLECTIONS["pathway_types"],
        list(PATHWAY_TYPES),
        [f"Pathway type: {p}" for p in PATHWAY_TYPES],
        [{"type": p} for p in PATHWAY_TYPES],
    )
    status["collections"]["difficulty_levels"] = upsert(
        ALE_COLLECTIONS["difficulty_levels"],
        list(DIFFICULTY_LEVELS),
        [f"Difficulty: {d}" for d in DIFFICULTY_LEVELS],
        [{"level": d} for d in DIFFICULTY_LEVELS],
    )
    return status
