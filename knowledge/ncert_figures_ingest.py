"""PyMuPDF-based NCERT figure / caption extraction (Knowledge Layer)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from knowledge.paths import INGEST_DIR


def _alt_from_caption(caption: str, page: int) -> str:
    cap = (caption or "").strip()
    if cap:
        return f"NCERT figure on page {page}: {cap}"
    return f"Educational diagram extracted from NCERT PDF page {page}."


def extract_figures_from_pdf(
    pdf_path: Path,
    *,
    max_figures: int = 40,
    min_bytes: int = 8_000,
) -> list[dict[str, Any]]:
    """
    Extract embedded images from an NCERT PDF with nearby caption heuristics.

    Requires pymupdf (fitz). Returns metadata + saved image paths under
    data/knowledge/ingested/figures/<pdf-stem>/.
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(str(pdf_path))

    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise RuntimeError(
            "PyMuPDF (pymupdf) required for figure extraction. "
            "Install: pip install pymupdf"
        ) from exc

    out_dir = INGEST_DIR / "figures" / pdf_path.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(str(pdf_path))
    figures: list[dict[str, Any]] = []
    fig_idx = 0

    for page_no in range(len(doc)):
        if len(figures) >= max_figures:
            break
        page = doc[page_no]
        page_text = page.get_text("text") or ""
        # Caption candidates: "Fig. 8.1", "Figure 3.2", etc.
        caption_hits = re.findall(
            r"((?:Fig(?:ure)?\.?\s*\d+\.?\d*)[^\n]{0,120})",
            page_text,
            flags=re.I,
        )
        images = page.get_images(full=True)
        for img_i, img in enumerate(images):
            if len(figures) >= max_figures:
                break
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.n > 4:  # CMYK etc.
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                raw = pix.tobytes("png")
            except Exception:
                continue
            if len(raw) < min_bytes:
                continue
            fig_idx += 1
            fname = f"p{page_no + 1:03d}_img{img_i + 1:02d}.png"
            path = out_dir / fname
            path.write_bytes(raw)
            caption = caption_hits[min(img_i, len(caption_hits) - 1)] if caption_hits else ""
            # Chapter heuristic from running headers
            chapter = 0
            ch_m = re.search(r"Chapter\s+(\d+)", page_text, re.I)
            if ch_m:
                chapter = int(ch_m.group(1))
            fig_num_m = re.search(r"(\d+\.\d+)", caption)
            figures.append(
                {
                    "id": f"{pdf_path.stem}-p{page_no + 1}-f{fig_idx}",
                    "source_pdf": str(pdf_path),
                    "page": page_no + 1,
                    "chapter": chapter,
                    "figure_number": fig_num_m.group(1) if fig_num_m else "",
                    "caption": caption.strip(),
                    "alt_text": _alt_from_caption(caption, page_no + 1),
                    "keywords": re.findall(r"[A-Za-z]{4,}", caption.lower())[:12],
                    "path": str(path),
                    "relative_path": str(path.relative_to(INGEST_DIR)) if str(path).startswith(str(INGEST_DIR)) else str(path),
                    "bytes": len(raw),
                }
            )

    doc.close()

    index_path = out_dir / "index.json"
    index_path.write_text(json.dumps(figures, indent=2), encoding="utf-8")
    return figures


def match_ingested_figures(lesson_text: str, topic: str = "", limit: int = 3) -> list[dict]:
    """Keyword match against any ingested figure indexes."""
    root = INGEST_DIR / "figures"
    if not root.is_dir():
        return []
    blob = f"{topic}\n{lesson_text}".lower()
    scored: list[tuple[int, dict]] = []
    for index in root.glob("*/index.json"):
        try:
            rows = json.loads(index.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for fig in rows:
            score = 0
            for kw in fig.get("keywords") or []:
                if kw in blob:
                    score += 2
            cap = (fig.get("caption") or "").lower()
            if cap and any(w in blob for w in cap.split() if len(w) > 4):
                score += 1
            if score and Path(fig.get("path") or "").is_file():
                scored.append((score, fig))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [f for _, f in scored[:limit]]
