"""Chroma-backed semantic question bank — extends JSON official items."""

from __future__ import annotations

from knowledge.paths import CHROMA_DIR
from knowledge.pilot_config import ACTIVE_PILOT, PilotScope
from knowledge.question_bank import load_official_items
from knowledge.types import OfficialMcq


class QuestionBankIndex:
    """Vector index over official questions with metadata filters."""

    def __init__(self, scope: PilotScope | None = None):
        self.scope = scope or ACTIVE_PILOT
        self._collection = None
        self._ok = False
        self._items = load_official_items(self.scope)
        self._init()

    def _init(self) -> None:
        try:
            import chromadb

            CHROMA_DIR.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            self._collection = client.get_or_create_collection(
                name=f"questions_{self.scope.pilot_id}",
                metadata={"hnsw:space": "cosine"},
            )
            self._ok = True
        except Exception:
            self._ok = False
            self._collection = None

    def ensure_index(self) -> dict:
        if not self._items:
            return {"backend": "empty", "indexed": 0}
        if not self._ok or self._collection is None:
            return {"backend": "keyword", "indexed": len(self._items), "message": "Chroma unavailable"}
        try:
            existing = self._collection.count()
            if existing >= len(self._items):
                return {"backend": "chromadb", "indexed": existing}
            ids, docs, metas = [], [], []
            for it in self._items:
                ids.append(it.item_id)
                docs.append(f"{it.topic}\n{it.question}\n{it.explanation}")
                metas.append(
                    {
                        "source": it.source,
                        "subject": it.subject,
                        "grade": it.grade,
                        "chapter": it.chapter,
                        "topic": it.topic[:200],
                        "question_type": it.question_type,
                        "bloom": it.bloom,
                        "difficulty": it.difficulty,
                        "marks": it.marks,
                        "year": it.year or "",
                        "board": it.board,
                        "learning_objective": (it.learning_objective or "")[:200],
                        "official_answer": (it.official_answer or "")[:200],
                    }
                )
            # upsert in batches
            self._collection.upsert(ids=ids, documents=docs, metadatas=metas)
            return {"backend": "chromadb", "indexed": len(ids)}
        except Exception as exc:
            self._ok = False
            return {"backend": "keyword", "indexed": len(self._items), "message": str(exc)}

    def retrieve(
        self,
        query: str,
        *,
        k: int = 6,
        chapter: int | None = None,
        question_type: str | None = None,
        difficulty: str | None = None,
    ) -> list[OfficialMcq]:
        self.ensure_index()
        by_id = {it.item_id: it for it in self._items}

        if self._ok and self._collection is not None and (query or "").strip():
            where: dict | None = None
            clauses = []
            if chapter is not None:
                clauses.append({"chapter": chapter})
            if question_type:
                clauses.append({"question_type": question_type})
            if difficulty:
                clauses.append({"difficulty": difficulty})
            if len(clauses) == 1:
                where = clauses[0]
            elif len(clauses) > 1:
                where = {"$and": clauses}
            try:
                res = self._collection.query(
                    query_texts=[query],
                    n_results=min(k, max(len(self._items), 1)),
                    where=where,
                )
                ids = (res.get("ids") or [[]])[0]
                out = [by_id[i] for i in ids if i in by_id]
                if out:
                    return out[:k]
            except Exception:
                pass

        # Keyword fallback
        from knowledge.question_bank import match_official_mcqs

        return match_official_mcqs(query, limit=k, scope=self.scope)


_qb_singleton: QuestionBankIndex | None = None


def get_question_index() -> QuestionBankIndex:
    global _qb_singleton
    if _qb_singleton is None:
        _qb_singleton = QuestionBankIndex()
    return _qb_singleton


def semantic_match_questions(topic: str, lesson_text: str = "", limit: int = 8) -> list[OfficialMcq]:
    idx = get_question_index()
    return idx.retrieve(f"{topic}\n{lesson_text[:500]}", k=limit)
