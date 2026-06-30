"""
Build a printable vocabulary concept map (SVG + Word table) in EduAdapt teal/navy branding.
"""

import html
import json
import math
from typing import Any


def _coerce_dict(content: Any) -> dict | None:
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        text = content.strip()
        if text.startswith("{"):
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
    return None

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
    if len(terms) < 1:
        for card in vocab.get("flashcards") or []:
            term = (card.get("front") or card.get("term") or "").strip()
            if term and term not in terms:
                terms.append(term)
    if len(terms) < 1:
        for row in vocab.get("picture_words") or []:
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
    return lines[:3]


def _hub_size(topic: str) -> tuple[int, int]:
    lines = _wrap_label(topic, 16)
    hub_w = min(340, max(180, max(len(line) for line in lines) * 11 + 40))
    hub_h = max(52, 24 + len(lines) * 24)
    return hub_w, hub_h


def build_vocabulary_concept_map_svg(vocab: Any) -> str:
    """
    Hub-and-spoke flowchart: navy topic box above the spoke origin; lines radiate
    from the bottom of the box to term nodes arranged below.
    """
    data = _coerce_dict(vocab) or {}
    topic, terms = _topic_and_terms(data)
    if not terms:
        terms = ["Key term 1", "Key term 2", "Key term 3"]

    width, height = 820, 580
    cx = width // 2
    topic_lines = _wrap_label(topic, 16)
    hub_w, hub_h = _hub_size(topic)
    hub_x = cx - hub_w // 2
    hub_y = 36

    # Spokes radiate from the bottom-centre of the hub box.
    origin_x, origin_y = cx, hub_y + hub_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Concept map for {html.escape(topic)}">',
        f'<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" '
        f'orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{TEAL}"/></marker></defs>',
        f'<rect width="100%" height="100%" fill="#fafcfd"/>',
    ]

    # Central topic box — label inside the navy box.
    parts.append(
        f'<rect x="{hub_x}" y="{hub_y}" width="{hub_w}" height="{hub_h}" rx="12" '
        f'fill="{NAVY}" stroke="{TEAL}" stroke-width="2"/>'
    )
    text_start_y = hub_y + 22 + (hub_h - len(topic_lines) * 24) // 2
    for index, line in enumerate(topic_lines):
        ty = text_start_y + index * 24
        parts.append(
            f'<text x="{cx}" y="{ty}" text-anchor="middle" font-family="{FONT}" '
            f'font-size="15" font-weight="700" fill="#ffffff">{html.escape(line)}</text>'
        )

    count = len(terms)
    radius_x = 300
    radius_y = 185
    ellipse_cy = origin_y + 195
    box_w, box_h = 140, 48

    for index, term in enumerate(terms):
        # Spread terms in the lower arc (avoid overlapping the hub above).
        if count == 1:
            angle = math.pi / 2
        else:
            angle = math.pi * 0.12 + (math.pi * 0.76) * index / (count - 1)
        tx = cx + radius_x * math.cos(angle)
        ty = ellipse_cy + radius_y * math.sin(angle)
        bx = tx - box_w // 2
        by = ty - box_h // 2
        fill = LIGHT_TEAL if index % 2 == 0 else LIGHT_BLUE

        # Line from hub bottom edge toward the term box top.
        target_x, target_y = tx, by
        parts.append(
            f'<line x1="{origin_x}" y1="{origin_y}" x2="{target_x}" y2="{target_y}" '
            f'stroke="{TEAL}" stroke-width="2" marker-end="url(#arrow)"/>'
        )
        parts.append(
            f'<rect x="{bx}" y="{by}" width="{box_w}" height="{box_h}" rx="10" '
            f'fill="{fill}" stroke="{TEAL}" stroke-width="2"/>'
        )
        label_lines = _wrap_label(term, 18)
        label_start = ty - 6 - (len(label_lines) - 1) * 8
        for line_index, line in enumerate(label_lines):
            ly = label_start + line_index * 16
            parts.append(
                f'<text x="{tx}" y="{ly}" text-anchor="middle" font-family="{FONT}" '
                f'font-size="12" font-weight="600" fill="{NAVY}">{html.escape(line)}</text>'
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


def render_concept_map_streamlit(vocab: Any) -> None:
    """Always-visible hub-and-spoke map in the app (SVG only — section title is elsewhere)."""
    import streamlit as st

    svg = build_vocabulary_concept_map_svg(vocab)
    st.markdown(
        f'<div style="display:flex;justify-content:center;align-items:center;'
        f'max-width:100%;overflow-x:auto;padding:0.5rem 0 1rem 0;">{svg.strip()}</div>',
        unsafe_allow_html=True,
    )


def add_vocabulary_concept_map_to_docx(doc, vocab: Any) -> None:
    """Section 7 — centred flowchart-style concept map for Word print."""
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt, RGBColor

    data = _coerce_dict(vocab) or {}
    topic, terms = _topic_and_terms(data)
    if not terms:
        terms = ["Key term 1", "Key term 2", "Key term 3"]

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
    data = _coerce_dict(vocab) or {}
    svg = build_vocabulary_concept_map_svg(data)
    return (
        '<h2>7. Concept Map</h2>'
        '<p style="text-align:center;color:#0B2E59;">Study how all vocabulary terms connect to the main topic.</p>'
        f'<div class="concept-map">{svg}</div>'
    )
