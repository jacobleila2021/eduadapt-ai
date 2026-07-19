"""ATIE Chroma — tutoring mode / depth catalogues."""

from __future__ import annotations

from typing import Any

from knowledge.paths import CHROMA_DIR

from engines.ai_tutor_intelligence_engine.schemas import EXPLANATION_DEPTHS, TUTOR_MODES

ATIE_COLLECTIONS = {
    "modes": "atie_tutor_modes",
    "depths": "atie_explanation_depths",
}


def rebuild_atie_index() -> dict[str, Any]:
    status: dict[str, Any] = {"ok": True, "collections": {}}
    try:
        import chromadb

        CHROMA_DIR.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "warning": str(exc), "collections": {}}

    def upsert(name: str, ids: list[str], docs: list[str]) -> dict[str, Any]:
        try:
            col = client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
            col.upsert(ids=ids, documents=docs, metadatas=[{"id": i} for i in ids])
            return {"collection": name, "count": len(ids), "ok": True}
        except Exception as exc:  # noqa: BLE001
            return {"collection": name, "ok": False, "error": str(exc)}

    status["collections"]["modes"] = upsert(
        ATIE_COLLECTIONS["modes"], list(TUTOR_MODES), [f"Tutor mode: {m}" for m in TUTOR_MODES]
    )
    status["collections"]["depths"] = upsert(
        ATIE_COLLECTIONS["depths"], list(EXPLANATION_DEPTHS), [f"Depth: {d}" for d in EXPLANATION_DEPTHS]
    )
    return status
