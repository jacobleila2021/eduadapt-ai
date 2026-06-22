"""
Build a printable vocabulary concept map (SVG + Word table) in EduAdapt teal/navy branding.
"""

import html
import math
from typing import Any

from structured_renderers import _coerce_dict

NAVY = "#0B2E59"
TEAL = "#008C95"
LIGHT_TEAL = "#e6f7f8"
LIGHT_BLUE = "#e3f2fd"
FONT = "Lexend, Arial, Verdana, sans-serif"


def _topic_and_terms(vocab: dict) -> tuple[str, list[str]]:
    topic = (vocab.get("topic") or "Lesson Topic").strip()
    terms: list[str] = []
    for word in vocab.get("word_wall") or []:
        term = (word.get("term") or "").strip()
        if term and term not in terms:
            terms.append(term)
    if len(terms) < 3:
        for row in vocab.get("reference_chart") or []:
            term = (row.get("term") or "").strip()
            if term and term not in terms:
                terms.append(term)
    return topic, terms[:12]


def _wrap_label(text: str, max_len: int = 14) -> list[str]:
    words = text.split()
    if not words:
        return [text[:max_len]]
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        if len(current) + 1 + len(word) <= max_len:
            current += f" {word}"
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines[:2]


def build_vocabulary_concept_map_svg(vocab: Any) -> str:
    """
    Hub-and-spoke flowchart: central topic (navy) with terms in teal boxes.
    Suitable for HTML inline embed and colour printing.
    """
    data = _coerce_dict(vocab) or {}
    topic, terms = _topic_and_terms(data)
    if not terms:
        terms = ["Key term 1", "Key term 2", "Key term 3"]

    width, height = 820, 520
    cx, cy = width // 2, height // 2 + 10
    hub_w, hub_h = 200, 56

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Concept map for {html.escape(topic)}">',
        f'<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" '
        f'orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{TEAL}"/></marker></defs>',
        f'<rect width="100%" height="100%" fill="#fafcfd"/>',
        f'<text x="{width//2}" y="36" text-anchor="middle" font-family="{FONT}" '
        f'font-size="18" font-weight="700" fill="{NAVY}">Concept Map</text>',
    ]

    # Central topic box
    hub_x = cx - hub_w // 2
    hub_y = cy - hub_h // 2
    parts.append(
        f'<rect x="{hub_x}" y="{hub_y}" width="{hub_w}" height="{hub_h}" rx="12" '
        f'fill="{NAVY}" stroke="{TEAL}" stroke-width="2"/>'
    )
    topic_lines = _wrap_label(topic, 18)
    for index, line in enumerate(topic_lines):
        ty = cy - 6 + index * 18
        parts.append(
            f'<text x="{cx}" y="{ty}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="15" font-weight="600" fill="#ffffff">{html.escape(line)}</text>'
        )

    count = len(terms)
    radius_x = 290
    radius_y = 190
    box_w, box_h = 128, 44

    for index, term in enumerate(terms):
        angle = -math.pi / 2 + (2 * math.pi * index / count)
        tx = cx + radius_x * math.cos(angle)
        ty = cy + radius_y * math.sin(angle)
        bx = tx - box_w // 2
        by = ty - box_h // 2
        fill = LIGHT_TEAL if index % 2 == 0 else LIGHT_BLUE

        parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{tx}" y2="{ty}" stroke="{TEAL}" '
            f'stroke-width="2" marker-end="url(#arrow)"/>'
        )
        parts.append(
            f'<rect x="{bx}" y="{by}" width="{box_w}" height="{box_h}" rx="10" '
            f'fill="{fill}" stroke="{TEAL}" stroke-width="2"/>'
        )
        label_lines = _wrap_label(term, 16)
        for line_index, line in enumerate(label_lines):
            ly = ty - 4 + line_index * 16
            parts.append(
                f'<text x="{tx}" y="{ly}" text-anchor="middle" font-family="{FONT}" '
                f'font-size="13" font-weight="600" fill="{NAVY}">{html.escape(line)}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)


def _shade_cell(cell, fill_hex: str) -> None:
    """Apply background colour to a Word table cell."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill_hex)
    shading.set(qn("w:val"), "clear")
    cell._tc.get_or_add_tcPr().append(shading)


def add_vocabulary_concept_map_to_docx(doc, vocab: Any) -> None:
    """Section 7 — centred flowchart-style concept map for Word print."""
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt, RGBColor

    data = _coerce_dict(vocab) or {}
    topic, terms = _topic_and_terms(data)
    if not terms:
        return

    heading = doc.add_heading("7. Concept Map", level=2)
    for run in heading.runs:
        run.font.name = "Arial"
        run.font.color.rgb = RGBColor(0x0B, 0x2E, 0x59)

    intro = doc.add_paragraph(
        "Study how all vocabulary terms connect to the main topic."
    )
    intro.alignment = WD_ALIGN_PARAGRAPH.CENTER

    hub = doc.add_table(rows=1, cols=1)
    hub.style = "Table Grid"
    hub_cell = hub.rows[0].cells[0]
    _shade_cell(hub_cell, "0B2E59")
    hub_para = hub_cell.paragraphs[0]
    hub_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    hub_run = hub_para.add_run(topic)
    hub_run.bold = True
    hub_run.font.name = "Arial"
    hub_run.font.size = Pt(16)
    hub_run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    doc.add_paragraph("")

    columns = 3
    rows_needed = (len(terms) + columns - 1) // columns
    grid = doc.add_table(rows=rows_needed, cols=columns)
    grid.style = "Table Grid"

    for index, term in enumerate(terms):
        row = grid.rows[index // columns]
        cell = row.cells[index % columns]
        fill = "E6F7F8" if index % 2 == 0 else "E3F2FD"
        _shade_cell(cell, fill)
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run(term)
        run.bold = True
        run.font.name = "Arial"
        run.font.size = Pt(13)
        run.font.color.rgb = RGBColor(0x0B, 0x2E, 0x59)

    note = doc.add_paragraph(
        "Tip: Download the HTML vocabulary file for the full arrow flowchart (best for colour printing)."
    )
    note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in note.runs:
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x00, 0x8C, 0x95)


def vocabulary_concept_map_html_block(vocab: Any) -> str:
    """Centered concept map section for HTML export."""
    svg = build_vocabulary_concept_map_svg(vocab)
    return (
        '<h2>7. Concept Map</h2>'
        '<p style="text-align:center;color:#0B2E59;">Study how all vocabulary terms connect to the main topic.</p>'
        f'<div class="concept-map">{svg}</div>'
    )
