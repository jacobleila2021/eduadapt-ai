"""Vector indexing — separate Chroma collections for KIE outputs."""

from __future__ import annotations

from typing import Any

from knowledge.paths import CHROMA_DIR


COLLECTION_NAMES = {
    "curriculum_chunks": "kie_curriculum_chunks",
    "question_bank": "kie_question_bank",
    "figures": "kie_figures",
    "formulas": "kie_formulas",
    "diagrams": "kie_diagrams",
    "vocabulary": "kie_vocabulary",
    "worked_examples": "kie_worked_examples",
    "misconceptions": "kie_misconceptions",
}


def _client():
    import chromadb

    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(CHROMA_DIR))


def _upsert(collection_key: str, ids: list[str], documents: list[str], metadatas: list[dict]) -> dict[str, Any]:
    if not ids:
        return {"collection": collection_key, "indexed": 0}
    try:
        client = _client()
        name = COLLECTION_NAMES.get(collection_key, f"kie_{collection_key}")
        col = client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
        # Chroma metadata values must be scalar
        clean_meta = []
        for m in metadatas:
            clean_meta.append({k: (v if isinstance(v, (str, int, float, bool)) else str(v)) for k, v in m.items()})
        col.upsert(ids=ids, documents=documents, metadatas=clean_meta)
        return {"collection": name, "indexed": len(ids), "backend": "chromadb"}
    except Exception as exc:
        return {"collection": collection_key, "indexed": 0, "backend": "none", "error": str(exc)}


def index_knowledge_package(package: dict[str, Any]) -> dict[str, Any]:
    """Index all KIE artifact types into dedicated collections."""
    status: dict[str, Any] = {}

    # Chunks
    chunks = package.get("text_chunks") or []
    status["curriculum_chunks"] = _upsert(
        "curriculum_chunks",
        [c["chunk_id"] for c in chunks],
        [c.get("text") or "" for c in chunks],
        [
            {
                "chapter": c.get("chapter") or 0,
                "board": c.get("board") or "",
                "grade": c.get("grade") or "",
                "subject": c.get("subject") or "",
                "source": c.get("source") or "",
            }
            for c in chunks
        ],
    )

    # Also refresh legacy KnowledgeRag seed path when chunks exist
    try:
        from knowledge.service import ensure_knowledge_index

        status["legacy_ncert_index"] = ensure_knowledge_index()
    except Exception as exc:
        status["legacy_ncert_index"] = {"error": str(exc)}

    # Questions
    questions = package.get("questions") or []
    status["question_bank"] = _upsert(
        "question_bank",
        [f"q-{i}-{hash(q.get('question','')) % 10**8}" for i, q in enumerate(questions)],
        [q.get("question") or "" for q in questions],
        [
            {
                "question_type": q.get("question_type") or "",
                "bloom": q.get("bloom") or "",
                "marks": q.get("marks") or 1,
                "chapter": q.get("chapter") or 0,
                "difficulty": q.get("difficulty") or "",
            }
            for q in questions
        ],
    )
    try:
        from knowledge.question_rag import get_question_index

        status["official_question_index"] = get_question_index().ensure_index()
    except Exception as exc:
        status["official_question_index"] = {"error": str(exc)}

    # Figures / diagrams
    figures = package.get("figures") or []
    status["figures"] = _upsert(
        "figures",
        [str(f.get("id") or f.get("figure_id") or f"fig-{i}") for i, f in enumerate(figures)],
        [
            f"{f.get('caption') or ''} {f.get('alt_text') or ''} {' '.join(f.get('keywords') or [])}".strip()
            or f"figure page {f.get('page')}"
            for f in figures
        ],
        [
            {
                "page": f.get("page") or 0,
                "chapter": f.get("chapter") or 0,
                "path": f.get("path") or "",
            }
            for f in figures
        ],
    )
    status["diagrams"] = status["figures"]  # same index for pilot

    # Formulas
    eqs = package.get("equations") or []
    status["formulas"] = _upsert(
        "formulas",
        [f"eq-{i}" for i in range(len(eqs))],
        [e.get("latex") or e.get("raw") or "" for e in eqs],
        [{"kind": e.get("kind") or "math"} for e in eqs],
    )

    # Vocabulary
    vocab = package.get("vocabulary") or []
    status["vocabulary"] = _upsert(
        "vocabulary",
        [f"v-{i}-{hash(t) % 10**6}" for i, t in enumerate(vocab)],
        list(vocab),
        [{"term": t} for t in vocab],
    )

    status["worked_examples"] = {"indexed": 0, "note": "populated when worked examples tagged"}
    status["misconceptions"] = {"indexed": 0, "note": "populated from engine common_mistakes later"}
    return status
