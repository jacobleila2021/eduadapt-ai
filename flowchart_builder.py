"""
Coloured Mermaid flowchart builder — replaces unreliable AI images with
lesson-accurate, labelled flowcharts (Alora navy/teal palette).

Uses Mermaid 10-safe syntax only (no HTML labels, no invalid node shapes).
"""

from __future__ import annotations

import html
import re
from typing import Any

NODE_CLASSES = [
    ("c1", "#e6f7f8", "#0B2E59", "#008C95"),
    ("c2", "#e3f2fd", "#0B2E59", "#008C95"),
    ("c3", "#ecfdf5", "#0B2E59", "#059669"),
    ("c4", "#fffbeb", "#0B2E59", "#d97706"),
    ("c5", "#f3e8ff", "#0B2E59", "#7c3aed"),
    ("c6", "#fce7f3", "#0B2E59", "#db2777"),
]


def _mermaid_safe(text: str, max_len: int = 28) -> str:
    """Plain-text label safe for Mermaid rectangle nodes."""
    cleaned = str(text or "")
    cleaned = cleaned.replace("&", "and")
    cleaned = re.sub(r'["\[\](){}|<>#;\\]', " ", cleaned)
    cleaned = re.sub(r"<[^>]+>", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return "Concept"
    if len(cleaned) > max_len:
        cleaned = cleaned[: max_len - 3].rstrip() + "..."
    return cleaned


def _quoted_label(text: str) -> str:
    """Wrap label in quotes only when needed."""
    safe = _mermaid_safe(text)
    if re.search(r"[^A-Za-z0-9 _-]", safe):
        return f'"{safe.replace(chr(34), chr(39))}"'
    return safe


def _append_class_defs(lines: list[str]) -> None:
    lines.append("  classDef hub fill:#0B2E59,color:#ffffff,stroke:#008C95,stroke-width:3px")
    lines.append("  classDef group fill:#008C95,color:#ffffff,stroke:#0B2E59,stroke-width:3px")
    for name, fill, text, stroke in NODE_CLASSES:
        lines.append(
            f"  classDef {name} fill:{fill},color:{text},stroke:{stroke},stroke-width:3px"
        )


def build_vocabulary_flowchart(vocab: dict) -> str:
    """Hub flowchart linking topic to vocabulary terms with colour-coded nodes."""
    topic = _mermaid_safe(vocab.get("topic") or "Lesson Vocabulary", 22)
    terms: list[str] = []

    for row in vocab.get("picture_words") or []:
        term = (row.get("term") or "").strip()
        if term and term not in terms:
            terms.append(term)

    if len(terms) < 3:
        for word in vocab.get("word_wall") or []:
            term = (word.get("term") or "").strip()
            if term and term not in terms:
                terms.append(term)

    terms = terms[:8]
    if not terms:
        terms = ["Key term 1", "Key term 2", "Key term 3"]

    lines = ["flowchart TD", f"  TOP([{topic}]):::hub"]
    for index, term in enumerate(terms):
        node_id = f"N{index}"
        cls = NODE_CLASSES[index % len(NODE_CLASSES)][0]
        label = _mermaid_safe(term, 22)
        lines.append(f"  TOP --> {node_id}[{_quoted_label(label)}]:::{cls}")

    _append_class_defs(lines)
    return "\n".join(lines)


def _svg_label(text: str, limit: int = 36) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(value) > limit:
        value = value[: limit - 1].rstrip() + "…"
    return html.escape(value)


def _water_cycle_visual_svg(topic: str) -> str:
    """Closed water-cycle flowchart: Evaporation → Condensation → Precipitation → Collection → Evaporation.

    Transpiration is a side loop into the atmosphere / condensation path.
    """
    title = _svg_label(topic, 54)
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="560" viewBox="0 0 960 560"
 role="img" aria-label="Closed water cycle flowchart">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#e8f6ff"/><stop offset="1" stop-color="#f7fbff"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#0B2E59" flood-opacity=".14"/>
    </filter>
    <marker id="arrow-cycle" markerWidth="12" markerHeight="12" refX="10" refY="5"
      orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#0B2E59"/></marker>
    <marker id="arrow-side" markerWidth="12" markerHeight="12" refX="10" refY="5"
      orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#059669"/></marker>
  </defs>
  <rect width="960" height="560" rx="24" fill="url(#sky)"/>
  <rect x="24" y="18" width="912" height="56" rx="16" fill="#0B2E59" filter="url(#shadow)"/>
  <text x="480" y="54" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="24" font-weight="700" fill="#fff">{title}</text>
  <text x="480" y="98" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="14" fill="#334155">Closed cycle: water moves continuously through these stages</text>

  <rect x="360" y="120" width="240" height="64" rx="16" fill="#0284c7" filter="url(#shadow)"/>
  <text x="480" y="148" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="13" fill="#e0f2fe">1</text>
  <text x="480" y="168" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="18" font-weight="700" fill="#fff">Evaporation</text>

  <rect x="640" y="250" width="240" height="64" rx="16" fill="#0B2E59" filter="url(#shadow)"/>
  <text x="760" y="278" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="13" fill="#cbd5e1">2</text>
  <text x="760" y="298" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="18" font-weight="700" fill="#fff">Condensation</text>

  <rect x="360" y="400" width="240" height="64" rx="16" fill="#0369a1" filter="url(#shadow)"/>
  <text x="480" y="428" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="13" fill="#e0f2fe">3</text>
  <text x="480" y="448" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="18" font-weight="700" fill="#fff">Precipitation</text>

  <rect x="80" y="250" width="240" height="64" rx="16" fill="#0ea5e9" filter="url(#shadow)"/>
  <text x="200" y="278" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="13" fill="#e0f2fe">4</text>
  <text x="200" y="298" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="18" font-weight="700" fill="#fff">Collection</text>

  <path d="M560 152 C640 152 700 180 740 250" fill="none" stroke="#0B2E59" stroke-width="5"
    marker-end="url(#arrow-cycle)"/>
  <path d="M760 314 C760 360 640 400 600 420" fill="none" stroke="#0B2E59" stroke-width="5"
    marker-end="url(#arrow-cycle)"/>
  <path d="M360 432 C280 432 220 380 200 314" fill="none" stroke="#0B2E59" stroke-width="5"
    marker-end="url(#arrow-cycle)"/>
  <path d="M200 250 C200 180 320 152 360 152" fill="none" stroke="#0B2E59" stroke-width="5"
    marker-end="url(#arrow-cycle)"/>

  <rect x="700" y="120" width="200" height="52" rx="14" fill="#059669" filter="url(#shadow)"/>
  <text x="800" y="152" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="16" font-weight="700" fill="#fff">Transpiration</text>
  <path d="M800 172 C820 210 800 230 780 250" fill="none" stroke="#059669" stroke-width="4"
    stroke-dasharray="8 7" marker-end="url(#arrow-side)"/>
  <text x="860" y="220" font-family="Lexend,Arial,sans-serif" font-size="12"
    fill="#047857">side loop → air</text>

  <text x="480" y="530" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="13" fill="#475569">Evaporation → Condensation → Precipitation → Collection → Evaporation</text>
</svg>""".strip()


def build_vocabulary_visual_svg(vocab: dict) -> str:
    """Premium deterministic visual for Picture Words."""
    topic = str(vocab.get("topic") or "Lesson Vocabulary")
    if "water cycle" in topic.lower():
        return _water_cycle_visual_svg(topic)

    rows = list(vocab.get("picture_words") or [])[:8]
    if not rows:
        rows = [{"term": "Key idea", "draw_this": "Main lesson concept"}]
    width = 960
    columns = 2
    card_w, card_h = 420, 106
    height = 118 + ((len(rows) + columns - 1) // columns) * 130 + 28
    colours = ["#06b6d4", "#2563eb", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="Picture words for {_svg_label(topic)}">',
        '<defs><filter id="card-shadow" x="-20%" y="-20%" width="140%" height="150%">'
        '<feDropShadow dx="0" dy="5" stdDeviation="6" flood-color="#0B2E59" flood-opacity=".14"/>'
        '</filter><linearGradient id="visual-bg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#f0f9ff"/><stop offset="1" stop-color="#f8fafc"/>'
        '</linearGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="24" fill="url(#visual-bg)"/>',
        '<rect x="28" y="22" width="904" height="66" rx="18" fill="#0B2E59"/>',
        f'<text x="480" y="63" text-anchor="middle" font-family="Lexend,Arial,sans-serif" '
        f'font-size="23" font-weight="700" fill="#fff">{_svg_label(topic, 60)}</text>',
    ]
    for index, row in enumerate(rows):
        col, grid_row = index % columns, index // columns
        x, y = 46 + col * 454, 112 + grid_row * 130
        accent = colours[index % len(colours)]
        term = _svg_label(row.get("term") or f"Key idea {index + 1}", 30)
        detail = _svg_label(row.get("draw_this") or row.get("label") or "Visualise this idea", 58)
        parts.extend(
            [
                f'<rect x="{x}" y="{y}" width="{card_w}" height="{card_h}" rx="18" '
                f'fill="#fff" filter="url(#card-shadow)"/>',
                f'<rect x="{x}" y="{y}" width="10" height="{card_h}" rx="5" fill="{accent}"/>',
                f'<circle cx="{x + 48}" cy="{y + 53}" r="24" fill="{accent}"/>',
                f'<text x="{x + 48}" y="{y + 60}" text-anchor="middle" '
                f'font-family="Lexend,Arial,sans-serif" font-size="18" font-weight="800" '
                f'fill="#fff">{index + 1}</text>',
                f'<text x="{x + 88}" y="{y + 42}" font-family="Lexend,Arial,sans-serif" '
                f'font-size="18" font-weight="750" fill="#0B2E59">{term}</text>',
                f'<text x="{x + 88}" y="{y + 70}" font-family="Lexend,Arial,sans-serif" '
                f'font-size="13" fill="#475569">{detail}</text>',
            ]
        )
    parts.append("</svg>")
    return "\n".join(parts)


def build_lesson_flowchart(lesson: dict) -> str:
    """Coloured concept flowchart — title-only nodes with generous spacing."""
    from study_diagram_builder import _study_nodes

    topic, nodes = _study_nodes(lesson if isinstance(lesson, dict) else {})
    topic_label = _mermaid_safe(topic, 28)

    lines = ["flowchart TD", f"  TOP([{topic_label}]):::hub"]

    if not nodes:
        _append_class_defs(lines)
        return "\n".join(lines)

    groups: dict[str, list[dict]] = {}
    for node in nodes:
        groups.setdefault(node.get("group") or "Core concepts", []).append(node)

    distinct = [g for g in groups if g != "Core concepts"]

    if len(distinct) >= 2 and len(groups) <= 4:
        for g_index, (group_name, items) in enumerate(sorted(groups.items())):
            gid = f"G{g_index}"
            lines.append(f"  TOP --> {gid}[{_quoted_label(group_name)}]:::group")
            for i_index, item in enumerate(items[:4]):
                nid = f"G{g_index}N{i_index}"
                cls = NODE_CLASSES[(g_index + i_index) % len(NODE_CLASSES)][0]
                title = _mermaid_safe(item.get("title", ""), 28)
                lines.append(f"  {gid} --> {nid}[{_quoted_label(title)}]:::{cls}")
    else:
        prev = "TOP"
        for index, node in enumerate(nodes[:6]):
            nid = f"S{index}"
            cls = NODE_CLASSES[index % len(NODE_CLASSES)][0]
            title = _mermaid_safe(node.get("title", ""), 28)
            lines.append(f"  {prev} --> {nid}[{_quoted_label(title)}]:::{cls}")
            prev = nid

    _append_class_defs(lines)
    return "\n".join(lines)


def build_study_flowchart(lesson: dict) -> str:
    """Vertical section flowchart — one short title per box, spaced for dyslexia readers."""
    from study_diagram_builder import _study_nodes

    topic, nodes = _study_nodes(lesson if isinstance(lesson, dict) else {})
    topic_label = _mermaid_safe(topic, 28)

    lines = ["flowchart TD", f"  TOP([{topic_label}]):::hub"]
    prev = "TOP"
    for index, node in enumerate(nodes[:8]):
        nid = f"ST{index}"
        cls = NODE_CLASSES[index % len(NODE_CLASSES)][0]
        title = _mermaid_safe(node.get("title", ""), 28)
        lines.append(f"  {prev} --> {nid}[{_quoted_label(title)}]:::{cls}")
        prev = nid

    _append_class_defs(lines)
    return "\n".join(lines)


def _looks_like_mermaid(text: str) -> bool:
    lowered = text.lower()
    return any(
        k in lowered
        for k in ("flowchart", "graph ", "mindmap", "sequencediagram", "timeline")
    )


def _ai_mermaid_is_safe(text: str) -> bool:
    """Reject AI diagrams that commonly trigger Mermaid parse errors."""
    if not text or not _looks_like_mermaid(text):
        return False
    lowered = text.lower()
    if "<br" in lowered or "<small" in lowered or "<div" in lowered:
        return False
    if '(["' in text or '(["' in text:
        return False
    if lowered.count("classdef") > 12:
        return False
    return True


def resolve_lesson_concept_flowchart(lesson: dict) -> str:
    """Always use Alora built coloured flowchart (AI mermaid was unreliable)."""
    return build_lesson_flowchart(lesson)


def resolve_lesson_study_flowchart(lesson: dict) -> str:
    """Study diagram as a section flowchart (always built for consistency)."""
    return build_study_flowchart(lesson)


def estimate_flowchart_height(diagram: str) -> int:
    """Dynamic iframe height from node count — avoids cramped or clipped flowcharts."""
    nodes = len(re.findall(r"\[[^\]]+\]", diagram))
    nodes = max(nodes, 3)
    return min(920, 140 + nodes * 100)


def flowchart_to_text(diagram: str) -> str:
    """Plain-text fallback for Word export."""
    lines = ["Visual flowchart:"]
    for match in re.finditer(r"\[([^\]]+)\]", diagram):
        label = match.group(1).strip('"')
        if label and not label.startswith("classDef"):
            lines.append(f"  - {label}")
    return "\n".join(lines) if len(lines) > 1 else "See online flowchart."
