"""CIE Chroma indexing — dedicated curriculum intelligence collections."""

from __future__ import annotations

from typing import Any

from engines.curriculum_intelligence_engine.graph import CurriculumKnowledgeGraph
from engines.curriculum_intelligence_engine.schemas import Competency
from knowledge.paths import CHROMA_DIR

CIE_COLLECTIONS = {
    "curriculum_concepts": "cie_curriculum_concepts",
    "learning_outcomes": "cie_learning_outcomes",
    "competencies": "cie_competencies",
    "prerequisites": "cie_prerequisites",
    "curriculum_maps": "cie_curriculum_maps",
    "cross_curriculum_links": "cie_cross_curriculum_links",
    "concept_resources": "cie_concept_resources",
    "assessment_links": "cie_assessment_links",
}


def _client():
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def _upsert(key: str, ids: list[str], documents: list[str], metadatas: list[dict]) -> dict[str, Any]:
    name = CIE_COLLECTIONS.get(key, f"cie_{key}")
    if not ids:
        return {"collection": name, "count": 0, "skipped": True}
    try:
        client = _client()
        col = client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
        clean_meta = []
        for m in metadatas:
            clean_meta.append(
                {k: (v if isinstance(v, (str, int, float, bool)) else str(v)) for k, v in m.items()}
            )
        col.upsert(ids=ids, documents=documents, metadatas=clean_meta)
        return {"collection": name, "count": len(ids), "ok": True, "backend": "chromadb"}
    except Exception as exc:  # noqa: BLE001
        return {"collection": name, "count": 0, "ok": False, "error": str(exc)}


def index_curriculum_graph(
    graph: CurriculumKnowledgeGraph,
    competencies: list[Competency] | None = None,
) -> dict[str, Any]:
    status: dict[str, Any] = {"ok": True, "collections": {}}
    try:
        _client()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "warning": f"chromadb unavailable: {exc}", "collections": {}}

    ids, docs, metas = [], [], []
    for c in graph.concepts.values():
        ids.append(c.concept_id)
        docs.append(f"{c.title}. {c.definition}")
        metas.append(
            {
                "chapter": c.chapter,
                "topic": c.topic or "",
                "board": c.board or "",
                "subject": c.subject or "",
                "difficulty": c.difficulty or "",
                "bloom": c.bloom or "",
            }
        )
    status["collections"]["curriculum_concepts"] = _upsert("curriculum_concepts", ids, docs, metas)

    ids, docs, metas = [], [], []
    for o in graph.outcomes.values():
        ids.append(o.outcome_id)
        docs.append(o.statement)
        metas.append(
            {
                "bloom": o.bloom,
                "dok": o.dok,
                "board": o.board,
                "chapter": o.chapter,
                "grade": o.grade or "",
            }
        )
    status["collections"]["learning_outcomes"] = _upsert("learning_outcomes", ids, docs, metas)

    comps = competencies or []
    ids, docs, metas = [], [], []
    for comp in comps:
        ids.append(comp.competency_id)
        docs.append(f"{comp.name}. {comp.description}")
        metas.append({"mastery_threshold": float(comp.mastery_threshold)})
    status["collections"]["competencies"] = _upsert("competencies", ids, docs, metas)

    ids, docs, metas = [], [], []
    for i, e in enumerate(graph.prerequisites):
        eid = f"prereq_{i}_{e.from_concept}_{e.to_concept}"
        ids.append(eid)
        docs.append(f"{e.from_concept} requires_before {e.to_concept}")
        metas.append(
            {"from_concept": e.from_concept, "to_concept": e.to_concept, "relation": e.relation}
        )
    status["collections"]["prerequisites"] = _upsert("prerequisites", ids, docs, metas)

    ids, docs, metas = [], [], []
    for i, link in enumerate(graph.cross_links):
        eid = f"xmap_{i}_{link.concept_id}_{link.board}"
        ids.append(eid)
        docs.append(f"{link.concept_id} ↔ {link.board} {link.label}")
        metas.append(
            {
                "concept_id": link.concept_id,
                "board": link.board,
                "programme": link.programme or "",
                "link_type": link.link_type,
            }
        )
    xstatus = _upsert("cross_curriculum_links", ids, docs, metas)
    status["collections"]["cross_curriculum_links"] = xstatus
    status["collections"]["curriculum_maps"] = xstatus
    return status
