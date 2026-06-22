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


def render_concept_map_streamlit(vocab: Any) -> None:
    """Always-visible hub-and-spoke map in the app (no iframe)."""
    import streamlit as st

    data = _coerce_dict(vocab) or {}
    topic, terms = _topic_and_terms(data)
    if not terms:
        terms = ["Key term 1", "Key term 2", "Key term 3"]

    st.markdown(
        f'<p style="text-align:center;font-weight:700;color:{NAVY};font-size:1.1rem;">'
        f"Concept Map</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div style="text-align:center;margin:0.75rem 0 1.25rem;">'
        f'<span style="display:inline-block;background:{NAVY};color:#fff;padding:14px 26px;'
        f'border-radius:12px;border:2px solid {TEAL};font-weight:700;">'
        f"{html.escape(topic)}</span></div>",
        unsafe_allow_html=True,
    )

    columns = st.columns(3)
    for index, term in enumerate(terms):
        fill = LIGHT_TEAL if index % 2 == 0 else LIGHT_BLUE
        with columns[index % 3]:
            st.markdown(
                f'<div style="text-align:center;background:{fill};border:2px solid {TEAL};'
                f"border-radius:10px;padding:10px 8px;margin:6px 0;color:{NAVY};"
                f'font-weight:600;font-size:0.95rem;">'
                f"&#8595; {html.escape(term)}</div>",
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
    topic, terms = _topic_and_terms(data)
    if not terms:
        terms = ["Key term 1", "Key term 2", "Key term 3"]
    svg = build_vocabulary_concept_map_svg(data)
    term_cells = "".join(
        f'<span style="display:inline-block;margin:6px;padding:10px 14px;background:'
        f'{"#e6f7f8" if i % 2 == 0 else "#e3f2fd"};border:2px solid #008C95;border-radius:10px;'
        f'color:#0B2E59;font-weight:600;">{html.escape(t)}</span>'
        for i, t in enumerate(terms)
    )
    return (
        '<h2>7. Concept Map</h2>'
        '<p style="text-align:center;color:#0B2E59;">Study how all vocabulary terms connect to the main topic.</p>'
        f'<div class="concept-map">{svg}</div>'
        f'<div style="text-align:center;margin-top:1rem;">'
        f'<span style="display:inline-block;background:#0B2E59;color:#fff;padding:12px 24px;'
        f'border-radius:12px;font-weight:700;">{html.escape(topic)}</span></div>'
        f'<div style="text-align:center;margin:1rem 0 2rem;line-height:2.2;">{term_cells}</div>'
    )
