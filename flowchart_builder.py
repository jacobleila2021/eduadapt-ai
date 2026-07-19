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
    """Deterministic, labelled water-cycle illustration (not an AI sketch)."""
    title = _svg_label(topic, 54)
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="520" viewBox="0 0 960 520"
 role="img" aria-label="Labelled water cycle diagram">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#dff5ff"/><stop offset="1" stop-color="#f8fcff"/>
    </linearGradient>
    <linearGradient id="water" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#0ea5e9"/><stop offset="1" stop-color="#06b6d4"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#0B2E59" flood-opacity=".16"/>
    </filter>
    <marker id="arrow-blue" markerWidth="12" markerHeight="12" refX="10" refY="5"
      orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#0284c7"/></marker>
    <marker id="arrow-navy" markerWidth="12" markerHeight="12" refX="10" refY="5"
      orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#0B2E59"/></marker>
  </defs>
  <rect width="960" height="520" rx="24" fill="url(#sky)"/>
  <rect x="24" y="20" width="912" height="58" rx="16" fill="#0B2E59" filter="url(#shadow)"/>
  <text x="480" y="57" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="24" font-weight="700" fill="#fff">{title}</text>

  <!-- Sun and energy -->
  <circle cx="122" cy="142" r="42" fill="#fbbf24" stroke="#f59e0b" stroke-width="5"/>
  <g stroke="#f59e0b" stroke-width="5" stroke-linecap="round">
    <path d="M122 82v-22M122 224v-22M62 142H40M204 142h-22
      M80 100L64 84M180 200l-16-16M164 100l16-16M80 184l-16 16"/>
  </g>
  <rect x="48" y="238" width="150" height="42" rx="21" fill="#fff" filter="url(#shadow)"/>
  <text x="123" y="264" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="15" font-weight="700" fill="#92400e">Sun supplies energy</text>

  <!-- Cloud / condensation -->
  <g filter="url(#shadow)">
    <circle cx="498" cy="150" r="42" fill="#fff"/><circle cx="550" cy="142" r="52" fill="#fff"/>
    <circle cx="603" cy="157" r="38" fill="#fff"/><rect x="462" y="156" width="177" height="48" rx="24" fill="#fff"/>
  </g>
  <rect x="480" y="214" width="150" height="40" rx="20" fill="#0B2E59"/>
  <text x="555" y="240" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="15" font-weight="700" fill="#fff">2 · Condensation</text>

  <!-- Land, plants and collection -->
  <path d="M0 400 Q170 320 335 390 Q500 462 665 366 Q820 280 960 350V520H0Z"
    fill="#86c56a"/>
  <path d="M595 408 Q720 345 960 360V520H520Q550 458 595 408Z" fill="#65a854"/>
  <path d="M0 428 Q230 390 455 438 Q650 478 960 420V520H0Z" fill="url(#water)"/>
  <path d="M0 452 Q230 414 455 462 Q650 502 960 444" fill="none"
    stroke="#bae6fd" stroke-width="8" opacity=".85"/>
  <rect x="675" y="452" width="178" height="42" rx="21" fill="#fff" filter="url(#shadow)"/>
  <text x="764" y="478" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="15" font-weight="700" fill="#075985">4 · Collection</text>

  <!-- Evaporation -->
  <path d="M310 414 C285 350 320 305 350 250" fill="none" stroke="#0284c7"
    stroke-width="6" stroke-linecap="round" stroke-dasharray="10 9" marker-end="url(#arrow-blue)"/>
  <path d="M375 425 C360 355 390 315 410 268" fill="none" stroke="#0284c7"
    stroke-width="4" stroke-linecap="round" stroke-dasharray="9 9" marker-end="url(#arrow-blue)"/>
  <rect x="240" y="286" width="160" height="42" rx="21" fill="#fff" filter="url(#shadow)"/>
  <text x="320" y="312" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="15" font-weight="700" fill="#075985">1 · Evaporation</text>

  <!-- Precipitation -->
  <path d="M585 215 C620 260 650 305 685 350" fill="none" stroke="#0B2E59"
    stroke-width="6" stroke-linecap="round" marker-end="url(#arrow-navy)"/>
  <g stroke="#38bdf8" stroke-width="5" stroke-linecap="round">
    <path d="M520 270l-10 24M552 277l-10 24M584 270l-10 24M616 279l-10 24"/>
  </g>
  <rect x="650" y="296" width="164" height="42" rx="21" fill="#fff" filter="url(#shadow)"/>
  <text x="732" y="322" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="15" font-weight="700" fill="#0B2E59">3 · Precipitation</text>

  <!-- Transpiration -->
  <g transform="translate(820 325)">
    <rect x="-5" y="20" width="10" height="76" rx="5" fill="#7c4a27"/>
    <circle cx="-22" cy="20" r="30" fill="#34a853"/><circle cx="20" cy="14" r="34" fill="#3fba63"/>
  </g>
  <path d="M820 346 C800 290 830 250 842 220" fill="none" stroke="#059669"
    stroke-width="4" stroke-dasharray="8 8" marker-end="url(#arrow-blue)"/>
  <text x="861" y="240" font-family="Lexend,Arial,sans-serif" font-size="13"
    font-weight="700" fill="#047857">Transpiration</text>
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
