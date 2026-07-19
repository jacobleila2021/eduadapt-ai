"""Production NCERT PDF ingestion — PyMuPDF text, structure, tables, figures."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from knowledge.ncert_figures_ingest import extract_figures_from_pdf
from knowledge.paths import INGEST_DIR
from knowledge.pilot_config import ACTIVE_PILOT, PilotScope
from knowledge.types import KnowledgeChunk


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]


def detect_chapter_and_headings(page_text: str) -> dict[str, Any]:
    chapter = 0
    ch_m = re.search(r"Chapter\s+(\d+)\s*[:.\-]?\s*([^\n]{0,80})?", page_text, re.I)
    title = ""
    if ch_m:
        chapter = int(ch_m.group(1))
        title = (ch_m.group(2) or "").strip()
    headings = re.findall(
        r"^(?:[0-9]+(?:\.[0-9]+)*\.?\s+|[A-Z][A-Z\s]{3,}|[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,6})\s*$",
        page_text,
        flags=re.M,
    )
    headings = [h.strip() for h in headings if 3 < len(h.strip()) < 80][:12]
    return {"chapter": chapter, "chapter_title": title, "headings": headings}


def extract_tables_from_page(page) -> list[dict]:
    """Best-effort table extraction via PyMuPDF find_tables when available."""
    tables: list[dict] = []
    try:
        finder = page.find_tables()
        for i, tab in enumerate(getattr(finder, "tables", []) or []):
            try:
                data = tab.extract()
            except Exception:
                continue
            if not data:
                continue
            tables.append({"table_index": i, "rows": data[:40], "n_rows": len(data)})
    except Exception:
        pass
    return tables


def ingest_pdf_pipeline(
    pdf_path: Path,
    scope: PilotScope | None = None,
    *,
    extract_figures: bool = True,
    max_figures: int = 40,
) -> dict[str, Any]:
    """
    Full ingest: text chunks + headings + tables + figures with content hashes.
    Keeps pypdf path available via knowledge.ncert_ingest.ingest_pdf_to_chunks fallback.
    """
    scope = scope or ACTIVE_PILOT
    pdf_path = Path(pdf_path)
    try:
        import fitz
    except ImportError as exc:
        raise RuntimeError("pymupdf required for production ingest") from exc

    doc = fitz.open(str(pdf_path))
    repo = INGEST_DIR / "repository" / pdf_path.stem
    repo.mkdir(parents=True, exist_ok=True)

    chunks: list[KnowledgeChunk] = []
    page_records: list[dict] = []
    seen_hashes: set[str] = set()

    for i in range(len(doc)):
        page = doc[i]
        text = (page.get_text("text") or "").strip()
        text = re.sub(r"\s+", " ", text)
        meta = detect_chapter_and_headings(text)
        tables = extract_tables_from_page(page)
        page_hash = _hash_bytes(text.encode("utf-8")[:8000])
        record = {
            "page": i + 1,
            "chapter": meta["chapter"],
            "chapter_title": meta["chapter_title"],
            "headings": meta["headings"],
            "tables": tables,
            "content_hash": page_hash,
            "char_count": len(text),
        }
        page_records.append(record)
        if len(text) >= 80:
            chunks.append(
                KnowledgeChunk(
                    chunk_id=f"pdf-{pdf_path.stem}-p{i + 1:03d}",
                    text=text[:4000],
                    chapter=meta["chapter"],
                    chapter_title=meta["chapter_title"] or pdf_path.stem,
                    page_start=i + 1,
                    source="NCERT PDF",
                    board=scope.board,
                    grade=scope.grade,
                    subject=scope.subject,
                    keywords=meta["headings"][:6],
                )
            )

    figures: list[dict] = []
    if extract_figures:
        figures = extract_figures_from_pdf(pdf_path, max_figures=max_figures)
        deduped: list[dict] = []
        for fig in figures:
            path = Path(fig.get("path") or "")
            if path.is_file():
                h = _hash_bytes(path.read_bytes())
                fig["content_hash"] = h
                if h in seen_hashes:
                    fig["duplicate"] = True
                    continue
                seen_hashes.add(h)
                fig["duplicate"] = False
                fig["topic"] = fig.get("caption") or fig.get("chapter_title") or ""
                fig["figure_id"] = fig.get("id")
                deduped.append(fig)
        figures = deduped

    doc.close()

    manifest = {
        "source_pdf": str(pdf_path),
        "stem": pdf_path.stem,
        "board": scope.board,
        "grade": scope.grade,
        "subject": scope.subject,
        "pages": page_records,
        "chunk_count": len(chunks),
        "figure_count": len(figures),
        "figures": figures,
    }
    manifest_path = repo / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Persist chunks for RAG reindex
    from knowledge.ncert_ingest import save_ingested_chunks

    chunks_path = save_ingested_chunks(chunks, f"{pdf_path.stem}_pipeline")
    manifest["chunks_path"] = str(chunks_path)
    manifest["manifest_path"] = str(manifest_path)
    return manifest
