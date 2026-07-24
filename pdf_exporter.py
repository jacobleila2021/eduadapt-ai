"""PDF export for Alora lessons — beta-ready teacher/student packs.

Uses fpdf2 when installed; otherwise emits a minimal valid text PDF
so beta workflows never lack a PDF path.
"""

from __future__ import annotations

import re
from typing import Any


def _plain(text: Any) -> str:
    raw = str(text or "")
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def _lesson_lines(title: str, content: Any, spec_id: str = "") -> list[str]:
    lines = [f"Alora AI — {title}", f"Adaptation: {spec_id or 'standard'}", ""]
    data = content if isinstance(content, dict) else {"text": str(content or "")}
    if data.get("big_idea"):
        lines.append("Opening")
        lines.append(_plain(data["big_idea"]))
        lines.append("")
    for sec in data.get("sections") or []:
        if not isinstance(sec, dict):
            continue
        lines.append(_plain(sec.get("title") or "Section"))
        lines.append(_plain(sec.get("body") or ""))
        lines.append("")
    if data.get("word_wall"):
        lines.append("Vocabulary")
        for row in data.get("word_wall") or []:
            if isinstance(row, dict):
                lines.append(
                    f"{row.get('term')}: {_plain(row.get('definition') or row.get('simple_explanation') or '')}"
                )
        lines.append("")
    pkg = data.get("diagram_package") if isinstance(data.get("diagram_package"), dict) else {}
    if pkg.get("caption"):
        lines.append("Diagram")
        lines.append(_plain(pkg.get("caption")))
        lines.append(_plain(pkg.get("practice_question") or ""))
    return [ln for ln in lines if ln is not None]


def _pdf_with_fpdf(lines: list[str]) -> bytes:
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    pdf.set_fill_color(255, 249, 238)  # cream
    pdf.rect(0, 0, 210, 297, "F")
    pdf.set_text_color(11, 46, 89)
    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, lines[0] if lines else "Alora AI Lesson")
    pdf.set_font("Helvetica", size=11)
    for line in lines[1:]:
        if not line:
            pdf.ln(4)
            continue
        # Helvetica core fonts are Latin-1; strip unsupported glyphs
        safe = line.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe)
    out = pdf.output()
    return bytes(out) if not isinstance(out, (bytes, bytearray)) else bytes(out)


def _escape_pdf_text(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def _pdf_minimal(lines: list[str]) -> bytes:
    """Minimal multi-page text PDF without third-party deps."""
    content_lines = []
    y = 800
    content_lines.append("BT /F1 11 Tf 50 800 Td")
    first = True
    for line in lines[:180]:
        safe = _escape_pdf_text(line[:110] or " ")
        if first:
            content_lines.append(f"({safe}) Tj")
            first = False
        else:
            content_lines.append(f"0 -14 Td ({safe}) Tj")
        y -= 14
        if y < 60:
            break
    content_lines.append("ET")
    stream = "\n".join(content_lines).encode("latin-1", "replace")
    objs = []
    objs.append(b"1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n")
    objs.append(b"2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n")
    objs.append(
        b"3 0 obj<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Contents 4 0 R /Resources<< /Font<< /F1 5 0 R >> >> >>endobj\n"
    )
    objs.append(f"4 0 obj<< /Length {len(stream)} >>stream\n".encode("latin-1") + stream + b"\nendstream\nendobj\n")
    objs.append(b"5 0 obj<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>endobj\n")
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objs:
        offsets.append(len(out))
        out.extend(obj)
    xref_pos = len(out)
    out.extend(f"xref\n0 {len(offsets)}\n".encode("latin-1"))
    out.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        out.extend(f"{off:010d} 00000 n \n".encode("latin-1"))
    out.extend(
        f"trailer<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode(
            "latin-1"
        )
    )
    return bytes(out)


def export_tab_pdf(title: str, content: Any, spec_id: str = "standard") -> bytes:
    """Return PDF bytes for one adaptation."""
    lines = _lesson_lines(title, content, spec_id)
    try:
        return _pdf_with_fpdf(lines)
    except Exception:
        return _pdf_minimal(lines)


def export_bundle_pdfs(adaptations: dict, base_name: str = "alora") -> dict[str, bytes]:
    """Map adaptation_id → PDF bytes."""
    out: dict[str, bytes] = {}
    for key, value in (adaptations or {}).items():
        if str(key).startswith("_") or not isinstance(value, dict):
            continue
        title = str(value.get("title") or value.get("topic") or base_name)
        out[key] = export_tab_pdf(title, value, key)
    return out
