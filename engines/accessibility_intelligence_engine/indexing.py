"""AIE Chroma indexing — accessibility profile & support catalogs."""

from __future__ import annotations

from typing import Any

from knowledge.paths import CHROMA_DIR

from engines.accessibility_intelligence_engine.adaptation_rules import RULES
from engines.accessibility_intelligence_engine.sensory_profiles import catalog

AIE_COLLECTIONS = {
    "profiles": "aie_learner_profiles_catalog",
    "supports": "aie_supports",
    "recommendations": "aie_recommendation_rules",
}


def _client():
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def _upsert(name: str, ids: list[str], documents: list[str], metadatas: list[dict]) -> dict[str, Any]:
    if not ids:
        return {"collection": name, "count": 0, "skipped": True}
    try:
        col = _client().get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
        clean = [
            {k: (v if isinstance(v, (str, int, float, bool)) else str(v)) for k, v in m.items()}
            for m in metadatas
        ]
        col.upsert(ids=ids, documents=documents, metadatas=clean)
        return {"collection": name, "count": len(ids), "ok": True}
    except Exception as exc:  # noqa: BLE001
        return {"collection": name, "count": 0, "ok": False, "error": str(exc)}


def rebuild_aie_index() -> dict[str, Any]:
    status: dict[str, Any] = {"ok": True, "collections": {}}
    try:
        _client()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "warning": str(exc), "collections": {}}

    ids, docs, metas = [], [], []
    for pid, meta in catalog().items():
        ids.append(pid)
        docs.append(f"{meta.get('label')}. supports: {', '.join(meta.get('supports') or [])}")
        metas.append({"presentation": meta.get("presentation") or "", "label": meta.get("label") or ""})
    status["collections"]["profiles"] = _upsert(AIE_COLLECTIONS["profiles"], ids, docs, metas)

    ids, docs, metas = [], [], []
    for rule in RULES:
        sid = rule["support_id"]
        ids.append(sid)
        docs.append(f"{rule['title']}. {rule['reason']}. {rule['evidence']}")
        metas.append({"category": rule["category"], "priority": int(rule["priority"])})
    status["collections"]["supports"] = _upsert(AIE_COLLECTIONS["supports"], ids, docs, metas)
    status["collections"]["recommendations"] = status["collections"]["supports"]
    return status
