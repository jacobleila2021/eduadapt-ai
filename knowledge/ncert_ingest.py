"""NCERT ingestion — PDF or bundled pilot seed."""

from __future__ import annotations

import json
import re
from pathlib import Path

from knowledge.paths import INGEST_DIR, SEED_DIR
from knowledge.pilot_config import ACTIVE_PILOT, PilotScope
from knowledge.types import KnowledgeChunk


def load_seed_chunks(scope: PilotScope | None = None) -> list[KnowledgeChunk]:
    scope = scope or ACTIVE_PILOT
    path = SEED_DIR / scope.seed_file
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    chunks: list[KnowledgeChunk] = []
    for row in data.get("chunks") or []:
        chunks.append(
            KnowledgeChunk(
                chunk_id=str(row["id"]),
                text=str(row["text"]),
                chapter=int(row.get("chapter") or 0),
                chapter_title=str(row.get("chapter_title") or ""),
                page_start=row.get("page_start"),
                source=str(row.get("source") or "NCERT"),
                board=str(data.get("board") or scope.board),
                grade=str(data.get("grade") or scope.grade),
                subject=str(data.get("subject") or scope.subject),
                keywords=list(row.get("keywords") or []),
            )
        )
    return chunks


def ingest_pdf_to_chunks(pdf_path: Path, scope: PilotScope | None = None) -> list[KnowledgeChunk]:
    """Extract text pages from an NCERT PDF (pilot — one page ≈ one chunk). Prefer PyMuPDF."""
    scope = scope or ACTIVE_PILOT
    pdf_path = Path(pdf_path)

    # Prefer PyMuPDF when available (better layout + optional figure side-car)
    try:
        import fitz

        doc = fitz.open(str(pdf_path))
        chunks: list[KnowledgeChunk] = []
        for i in range(len(doc)):
            page = doc[i]
            text = (page.get_text("text") or "").strip()
            if len(text) < 80:
                continue
            text = re.sub(r"\s+", " ", text)
            chapter = 0
            ch_m = re.search(r"Chapter\s+(\d+)", text, re.I)
            if ch_m:
                chapter = int(ch_m.group(1))
            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"pdf-{pdf_path.stem}-p{i + 1:03d}",
                    text=text[:4000],
                    chapter=chapter,
                    chapter_title=pdf_path.stem,
                    page_start=i + 1,
                    source="NCERT PDF",
                    board=scope.board,
                    grade=scope.grade,
                    subject=scope.subject,
                    keywords=[],
                )
            )
        doc.close()
        # Side-car figure extraction (best-effort)
        try:
            from knowledge.ncert_figures_ingest import extract_figures_from_pdf

            extract_figures_from_pdf(pdf_path)
        except Exception:
            pass
        return chunks
    except ImportError:
        pass

    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("pypdf or pymupdf required for PDF ingest") from exc

    reader = PdfReader(str(pdf_path))
    chunks = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if len(text) < 80:
            continue
        text = re.sub(r"\s+", " ", text)
        chunks.append(
            KnowledgeChunk(
                chunk_id=f"pdf-{pdf_path.stem}-p{i:03d}",
                text=text[:4000],
                chapter=0,
                chapter_title=pdf_path.stem,
                page_start=i,
                source="NCERT PDF",
                board=scope.board,
                grade=scope.grade,
                subject=scope.subject,
                keywords=[],
            )
        )
    return chunks


def save_ingested_chunks(chunks: list[KnowledgeChunk], label: str) -> Path:
    INGEST_DIR.mkdir(parents=True, exist_ok=True)
    out = INGEST_DIR / f"{label}.json"
    payload = [
        {
            "chunk_id": c.chunk_id,
            "text": c.text,
            "chapter": c.chapter,
            "chapter_title": c.chapter_title,
            "page_start": c.page_start,
            "source": c.source,
            "board": c.board,
            "grade": c.grade,
            "subject": c.subject,
            "keywords": c.keywords,
        }
        for c in chunks
    ]
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out
