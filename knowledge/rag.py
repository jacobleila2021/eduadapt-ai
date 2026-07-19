"""Chroma RAG + keyword fallback for NCERT pilot."""

from __future__ import annotations

import re
from typing import Any

from knowledge.ncert_ingest import load_seed_chunks
from knowledge.paths import CHROMA_DIR
from knowledge.pilot_config import ACTIVE_PILOT, PilotScope
from knowledge.types import KnowledgeChunk, RagHit


def _tokenize(text: str) -> set[str]:
    return {w.lower() for w in re.findall(r"[a-zA-Z]{4,}", text)}


def _keyword_retrieve(query: str, chunks: list[KnowledgeChunk], k: int = 6) -> list[RagHit]:
    q_tokens = _tokenize(query)
    if not q_tokens:
        return []
    scored: list[tuple[float, KnowledgeChunk]] = []
    for chunk in chunks:
        c_tokens = _tokenize(chunk.text + " " + " ".join(chunk.keywords))
        overlap = len(q_tokens & c_tokens)
        if overlap:
            scored.append((overlap / max(len(q_tokens), 1), chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    hits: list[RagHit] = []
    for score, chunk in scored[:k]:
        hits.append(
            RagHit(
                chunk_id=chunk.chunk_id,
                text=chunk.text[:1200],
                score=round(score, 3),
                citation=chunk.citation(),
                chapter_title=chunk.chapter_title,
                metadata={
                    "chapter": chunk.chapter,
                    "source": chunk.source,
                    "grade": chunk.grade,
                    "subject": chunk.subject,
                },
            )
        )
    return hits


class KnowledgeRag:
    def __init__(self, scope: PilotScope | None = None) -> None:
        self.scope = scope or ACTIVE_PILOT
        self._chunks = load_seed_chunks(self.scope)
        self._chroma_ok = False
        self._collection: Any = None
        self._init_chroma()

    def _init_chroma(self) -> None:
        try:
            import chromadb

            CHROMA_DIR.mkdir(parents=True, exist_ok=True)
            client = chromadb.PersistentClient(path=str(CHROMA_DIR))
            self._collection = client.get_or_create_collection(
                name=self.scope.chroma_collection,
                metadata={"pilot_id": self.scope.pilot_id},
            )
            self._chroma_ok = True
        except Exception:
            self._chroma_ok = False

    @property
    def chunk_count(self) -> int:
        return len(self._chunks)

    def ensure_index(self) -> dict:
        """Index seed chunks into Chroma if empty."""
        if not self._chunks:
            return {"indexed": 0, "backend": "none", "message": "No seed chunks"}

        if not self._chroma_ok:
            return {
                "indexed": len(self._chunks),
                "backend": "keyword_fallback",
                "message": "Chroma unavailable — using keyword retrieval",
            }

        try:
            existing = self._collection.count()
            if existing >= len(self._chunks):
                return {
                    "indexed": existing,
                    "backend": "chromadb",
                    "message": "Index already built",
                }
            ids = [c.chunk_id for c in self._chunks]
            docs = [c.text for c in self._chunks]
            metas = [
                {
                    "chapter": c.chapter,
                    "chapter_title": c.chapter_title,
                    "page_start": c.page_start or 0,
                    "source": c.source,
                    "board": c.board,
                    "grade": c.grade,
                    "subject": c.subject,
                    "citation": c.citation(),
                }
                for c in self._chunks
            ]
            self._collection.upsert(ids=ids, documents=docs, metadatas=metas)
            return {
                "indexed": self._collection.count(),
                "backend": "chromadb",
                "message": "Pilot index built",
            }
        except Exception as exc:
            self._chroma_ok = False
            return {
                "indexed": len(self._chunks),
                "backend": "keyword_fallback",
                "message": f"Chroma index failed: {exc}",
            }

    def retrieve(self, query: str, k: int = 6) -> list[RagHit]:
        if not query.strip():
            return []

        if self._chroma_ok and self._collection is not None:
            try:
                if self._collection.count() == 0:
                    self.ensure_index()
                result = self._collection.query(query_texts=[query], n_results=min(k, max(self.chunk_count, 1)))
                hits: list[RagHit] = []
                docs = (result.get("documents") or [[]])[0]
                metas = (result.get("metadatas") or [[]])[0]
                ids = (result.get("ids") or [[]])[0]
                dists = (result.get("distances") or [[]])[0]
                for i, doc in enumerate(docs):
                    meta = metas[i] if i < len(metas) else {}
                    score = 1.0 - (dists[i] if i < len(dists) else 0.0)
                    hits.append(
                        RagHit(
                            chunk_id=ids[i] if i < len(ids) else f"hit-{i}",
                            text=str(doc)[:1200],
                            score=round(max(score, 0.0), 3),
                            citation=str(meta.get("citation") or "[NCERT]"),
                            chapter_title=str(meta.get("chapter_title") or ""),
                            metadata=meta,
                        )
                    )
                if hits:
                    return hits
            except Exception:
                self._chroma_ok = False

        return _keyword_retrieve(query, self._chunks, k=k)
