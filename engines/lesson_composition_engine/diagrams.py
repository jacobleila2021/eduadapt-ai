"""Publication-quality SVG flowcharts and concept maps for LCE.

Professional SVG only by default. Mermaid is not emitted unless explicitly requested.
"""

from __future__ import annotations

import html
import math
from typing import Any

NAVY = "#0B2E59"
TEAL = "#008C95"
INK = "#1e293b"
MUTED = "#64748b"
WHITE = "#ffffff"
CARD_FILLS = (
    "#e6f7f8",
    "#e3f2fd",
    "#ecfdf5",
    "#fff7ed",
    "#fdf2f8",
    "#f5f3ff",
    "#fef9c3",
    "#eef2ff",
)
FONT = "Georgia, 'Times New Roman', serif"
UI_FONT = "Segoe UI, Candara, Calibri, sans-serif"


def _esc(text: str) -> str:
    return html.escape(str(text or ""), quote=True)


def _wrap(text: str, width: int = 18) -> list[str]:
    words = str(text or "").split()
    if not words:
        return [""]
    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        if len(cur) + 1 + len(w) <= width:
            cur += f" {w}"
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines[:3]


def _rounded_rect(x: float, y: float, w: float, h: float, fill: str, stroke: str, r: int = 14) -> str:
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" ry="{r}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    )


def _text_block(x: float, y: float, lines: list[str], *, fill: str = INK, size: int = 13, weight: str = "600") -> str:
    parts = [
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" '
        f'font-family="{UI_FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}">'
    ]
    for i, line in enumerate(lines):
        dy = 0 if i == 0 else 16
        parts.append(f'<tspan x="{x:.1f}" dy="{dy}">{_esc(line)}</tspan>')
    parts.append("</text>")
    return "".join(parts)


def build_educational_flowchart_svg(
    topic: str,
    stages: list[str],
    *,
    subtitle: str = "Learning pathway",
) -> str:
    """Vertical premium flowchart with rounded nodes and consistent spacing."""
    nodes = [str(s).strip() for s in stages if str(s).strip()][:8]
    if not nodes:
        nodes = ["Explore", "Explain", "Practise", "Apply"]
    width = 420
    top = 56
    gap = 78
    node_w, node_h = 260, 52
    height = top + len(nodes) * gap + 40
    cx = width / 2
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{_esc(topic)} flowchart">'
        f'<rect width="100%" height="100%" fill="#f8fafc"/>'
        f'<text x="{cx}" y="28" text-anchor="middle" font-family="{FONT}" '
        f'font-size="18" font-weight="700" fill="{NAVY}">{_esc(topic)}</text>'
        f'<text x="{cx}" y="46" text-anchor="middle" font-family="{UI_FONT}" '
        f'font-size="11" fill="{MUTED}">{_esc(subtitle)}</text>'
    ]
    for i, label in enumerate(nodes):
        y = top + i * gap
        x = cx - node_w / 2
        fill = CARD_FILLS[i % len(CARD_FILLS)]
        stroke = TEAL if i else NAVY
        parts.append(_rounded_rect(x, y, node_w, node_h, fill, stroke, r=16))
        lines = _wrap(label, 22)
        text_y = y + node_h / 2 - (len(lines) - 1) * 8
        parts.append(_text_block(cx, text_y, lines, fill=NAVY, size=14))
        if i < len(nodes) - 1:
            y1 = y + node_h
            y2 = y + gap
            parts.append(
                f'<line x1="{cx}" y1="{y1}" x2="{cx}" y2="{y2 - 4}" '
                f'stroke="{TEAL}" stroke-width="2.5"/>'
                f'<polygon points="{cx-6},{y2-10} {cx+6},{y2-10} {cx},{y2-2}" fill="{TEAL}"/>'
            )
    parts.append("</svg>")
    return "".join(parts)


def build_concept_map_svg(
    topic: str,
    concepts: list[str],
    *,
    relationships: list[tuple[str, str, str]] | None = None,
) -> str:
    """Hierarchical radial concept map with legend."""
    nodes = [str(c).strip() for c in concepts if str(c).strip()][:10]
    if not nodes:
        nodes = ["Key idea", "Example", "Practice"]
    width, height = 640, 440
    cx, cy = width / 2, height / 2 + 10
    hub_r = 54
    orbit = 150 if len(nodes) <= 6 else 165
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{_esc(topic)} concept map">'
        f'<rect width="100%" height="100%" fill="#f8fafc"/>'
        f'<text x="{cx}" y="28" text-anchor="middle" font-family="{FONT}" '
        f'font-size="18" font-weight="700" fill="{NAVY}">{_esc(topic)}</text>'
        f'<text x="24" y="{height - 18}" font-family="{UI_FONT}" font-size="11" fill="{MUTED}">'
        f"Legend: centre = topic · outer nodes = concepts · lines = relationships</text>"
    ]
    # spokes first
    positions: list[tuple[float, float]] = []
    for i, _ in enumerate(nodes):
        angle = -math.pi / 2 + (2 * math.pi * i / max(len(nodes), 1))
        x = cx + orbit * math.cos(angle)
        y = cy + orbit * math.sin(angle)
        positions.append((x, y))
        parts.append(
            f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" '
            f'stroke="#94a3b8" stroke-width="1.8"/>'
        )
    # hub
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{hub_r}" fill="{NAVY}" stroke="{TEAL}" stroke-width="3"/>')
    parts.append(_text_block(cx, cy - 6, _wrap(topic, 12), fill=WHITE, size=12, weight="700"))
    # concept nodes
    for i, (label, (x, y)) in enumerate(zip(nodes, positions)):
        fill = CARD_FILLS[i % len(CARD_FILLS)]
        nw, nh = 118, 46
        parts.append(_rounded_rect(x - nw / 2, y - nh / 2, nw, nh, fill, TEAL, r=12))
        parts.append(_text_block(x, y - 4, _wrap(label, 14), fill=NAVY, size=12))
    # optional relationship labels (first few)
    for a, b, rel in (relationships or [])[:4]:
        if a in nodes and b in nodes:
            ia, ib = nodes.index(a), nodes.index(b)
            ax, ay = positions[ia]
            bx, by = positions[ib]
            mx, my = (ax + bx) / 2, (ay + by) / 2
            parts.append(
                f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" '
                f'font-family="{UI_FONT}" font-size="10" fill="{MUTED}">{_esc(rel)}</text>'
            )
    parts.append("</svg>")
    return "".join(parts)


def build_vocabulary_concept_map_svg(
    topic: str,
    terms: list[str],
    *,
    mode: str = "concept_map",
) -> str:
    clean = [str(t).strip() for t in terms if str(t).strip()][:10]
    if mode == "flowchart":
        return build_educational_flowchart_svg(topic, clean or ["Term 1", "Term 2", "Term 3"], subtitle="Vocabulary pathway")
    return build_concept_map_svg(topic, clean)


def build_subject_flowchart(subject: str, topic: str, stages: list[str] | None = None) -> str:
    from engines.lesson_composition_engine.contracts import subject_sequence

    seq = stages or [s.replace("_", " ").title() for s in subject_sequence(subject)]
    return build_educational_flowchart_svg(topic, list(seq), subtitle=f"{subject.title()} learning flow")


def prefer_svg_over_mermaid(lesson: dict[str, Any], *, allow_mermaid: bool = False) -> dict[str, Any]:
    """Ensure lesson carries SVG diagrams; clear Mermaid unless explicitly allowed."""
    out = dict(lesson)
    if out.get("flowchart_svg") and not out.get("svg_diagram"):
        out["svg_diagram"] = out["flowchart_svg"]
    if out.get("concept_map_svg") and not out.get("svg_diagram"):
        out["svg_diagram"] = out["concept_map_svg"]
    if not allow_mermaid:
        out["mermaid_diagram"] = ""
    return out
