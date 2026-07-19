"""AME Chroma collections — assessment intelligence indexes."""

from __future__ import annotations

from typing import Any

from knowledge.paths import CHROMA_DIR

from engines.assessment_mastery_engine.misconceptions import list_misconceptions, load_misconception_bank

AME_COLLECTIONS = {
    "assessment_items": "ame_assessment_items",
    "competencies": "ame_competencies",
    "mastery_records": "ame_mastery_records",
    "misconceptions": "ame_misconceptions",
    "interventions": "ame_interventions",
    "revision_resources": "ame_revision_resources",
    "official_answers": "ame_official_answers",
}


def _client():
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def _upsert(key: str, ids: list[str], documents: list[str], metadatas: list[dict]) -> dict[str, Any]:
    name = AME_COLLECTIONS.get(key, f"ame_{key}")
    if not ids:
        return {"collection": name, "count": 0, "skipped": True}
    try:
        client = _client()
        col = client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
        clean = [
            {k: (v if isinstance(v, (str, int, float, bool)) else str(v)) for k, v in m.items()}
            for m in metadatas
        ]
        col.upsert(ids=ids, documents=documents, metadatas=clean)
        return {"collection": name, "count": len(ids), "ok": True}
    except Exception as exc:  # noqa: BLE001
        return {"collection": name, "count": 0, "ok": False, "error": str(exc)}


def rebuild_ame_index() -> dict[str, Any]:
    status: dict[str, Any] = {"ok": True, "collections": {}}
    try:
        _client()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "warning": str(exc), "collections": {}}

    # Official items
    try:
        from knowledge.question_bank import load_official_items

        items = load_official_items()
        ids, docs, metas = [], [], []
        oids, odocs, ometas = [], [], []
        for it in items:
            ids.append(it.item_id)
            docs.append(it.question)
            metas.append(
                {
                    "bloom": it.bloom or "",
                    "difficulty": it.difficulty or "",
                    "chapter": it.chapter,
                    "topic": it.topic or "",
                    "question_type": it.question_type or "",
                    "board": it.board or "",
                }
            )
            oids.append(f"ans_{it.item_id}")
            odocs.append(f"{it.question} => {it.official_answer}")
            ometas.append({"item_id": it.item_id, "source": it.source or ""})
        status["collections"]["assessment_items"] = _upsert("assessment_items", ids, docs, metas)
        status["collections"]["official_answers"] = _upsert("official_answers", oids, odocs, ometas)
    except Exception as exc:  # noqa: BLE001
        status["collections"]["assessment_items"] = {"ok": False, "error": str(exc)}

    # Misconceptions + interventions
    misc = list_misconceptions()
    ids, docs, metas = [], [], []
    for m in misc:
        ids.append(m["misconception_id"])
        docs.append(f"{m['label']}. {m.get('evidence_template') or ''}")
        metas.append({"concept_id": m.get("concept_id") or "", "bloom": m.get("bloom") or ""})
    status["collections"]["misconceptions"] = _upsert("misconceptions", ids, docs, metas)

    bank = load_misconception_bank()
    ints = bank.get("interventions") or []
    ids, docs, metas = [], [], []
    for i in ints:
        ids.append(i["intervention_id"])
        docs.append(f"{i.get('title')}. {i.get('description') or ''}")
        metas.append({"kind": i.get("kind") or "", "concept_id": i.get("concept_id") or ""})
    status["collections"]["interventions"] = _upsert("interventions", ids, docs, metas)
    status["collections"]["revision_resources"] = status["collections"]["interventions"]

    # CIE competencies mirror
    try:
        from engines.curriculum_intelligence_engine.intelligence import get_runtime

        comps = get_runtime()["competencies"]
        ids, docs, metas = [], [], []
        for c in comps:
            ids.append(c.competency_id)
            docs.append(f"{c.name}. {c.description}")
            metas.append({"mastery_threshold": float(c.mastery_threshold)})
        status["collections"]["competencies"] = _upsert("competencies", ids, docs, metas)
    except Exception as exc:  # noqa: BLE001
        status["collections"]["competencies"] = {"ok": False, "error": str(exc)}

    return status
