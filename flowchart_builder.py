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


def _is_water_cycle_topic(topic: str, extra: str = "") -> bool:
    blob = f"{topic} {extra}".lower()
    return any(
        k in blob
        for k in (
            "water cycle",
            "earth's water",
            "evaporat",
            "condens",
            "precipitat",
            "water vapour",
            "water vapor",
        )
    )


def _water_cycle_visual_svg(topic: str) -> str:
    """Pictorial water-cycle diagram: sun, lake, vapour, cloud, rain — not boxes only."""
    title = _svg_label(topic or "The Water Cycle", 54)
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" width="960" height="580" viewBox="0 0 960 580"
 role="img" aria-label="Pictorial water cycle diagram">
  <defs>
    <linearGradient id="wc-sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#bfdbfe"/><stop offset="0.55" stop-color="#e0f2fe"/>
      <stop offset="1" stop-color="#f0fdf4"/>
    </linearGradient>
    <linearGradient id="wc-water" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#38bdf8"/><stop offset="1" stop-color="#0369a1"/>
    </linearGradient>
    <linearGradient id="wc-sun" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fde68a"/><stop offset="1" stop-color="#f59e0b"/>
    </linearGradient>
    <filter id="wc-shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#0B2E59" flood-opacity=".16"/>
    </filter>
    <marker id="wc-arrow" markerWidth="11" markerHeight="11" refX="9" refY="5"
      orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#0B2E59"/></marker>
    <marker id="wc-arrow-g" markerWidth="11" markerHeight="11" refX="9" refY="5"
      orient="auto"><path d="M0,0 L10,5 L0,10 Z" fill="#047857"/></marker>
  </defs>
  <rect width="960" height="580" rx="24" fill="url(#wc-sky)"/>
  <rect x="24" y="16" width="912" height="52" rx="14" fill="#0B2E59" filter="url(#wc-shadow)"/>
  <text x="480" y="50" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="22" font-weight="700" fill="#fff">{title}</text>
  <text x="480" y="88" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="13" fill="#334155">Picture the journey: sun warms water → vapour rises → cloud forms → rain falls → water collects</text>

  <!-- Ground / hills -->
  <ellipse cx="480" cy="520" rx="420" ry="48" fill="#86efac" opacity=".55"/>
  <path d="M40 470 Q180 430 320 455 T620 448 T920 470 L920 580 L40 580 Z" fill="#bbf7d0"/>

  <!-- Lake / Collection -->
  <ellipse cx="320" cy="470" rx="170" ry="48" fill="url(#wc-water)" filter="url(#wc-shadow)"/>
  <ellipse cx="320" cy="458" rx="150" ry="22" fill="#7dd3fc" opacity=".55"/>
  <text x="320" y="476" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="15" font-weight="700" fill="#fff">Collection</text>
  <text x="320" y="530" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="12" fill="#0c4a6e">rivers · lakes · oceans</text>

  <!-- Sun (drives evaporation) -->
  <g filter="url(#wc-shadow)">
    <circle cx="140" cy="160" r="42" fill="url(#wc-sun)"/>
    <g stroke="#f59e0b" stroke-width="4" stroke-linecap="round">
      <line x1="140" y1="95" x2="140" y2="78"/><line x1="140" y1="242" x2="140" y2="225"/>
      <line x1="75" y1="160" x2="58" y2="160"/><line x1="222" y1="160" x2="205" y2="160"/>
      <line x1="94" y1="114" x2="82" y2="102"/><line x1="186" y1="206" x2="198" y2="218"/>
      <line x1="186" y1="114" x2="198" y2="102"/><line x1="94" y1="206" x2="82" y2="218"/>
    </g>
  </g>
  <text x="140" y="230" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="12" font-weight="600" fill="#92400e">Sun's heat</text>

  <!-- Evaporation: wavy rising vapour -->
  <path d="M260 420 C250 380 280 340 270 300" fill="none" stroke="#0284c7" stroke-width="3.5"
    stroke-dasharray="5 6" marker-end="url(#wc-arrow)"/>
  <path d="M300 415 C310 375 290 335 305 295" fill="none" stroke="#38bdf8" stroke-width="3"
    stroke-dasharray="4 5" marker-end="url(#wc-arrow)"/>
  <path d="M340 420 C355 375 330 340 350 300" fill="none" stroke="#0284c7" stroke-width="3"
    stroke-dasharray="5 6" marker-end="url(#wc-arrow)"/>
  <text x="220" y="340" font-family="Lexend,Arial,sans-serif" font-size="15"
    font-weight="700" fill="#0369a1">1. Evaporation</text>
  <text x="220" y="358" font-family="Lexend,Arial,sans-serif" font-size="11"
    fill="#475569">liquid → water vapour</text>

  <!-- Tree + Transpiration -->
  <rect x="520" y="390" width="16" height="70" rx="4" fill="#92400e"/>
  <ellipse cx="528" cy="360" rx="46" ry="42" fill="#16a34a"/>
  <ellipse cx="500" cy="375" rx="28" ry="24" fill="#22c55e"/>
  <ellipse cx="556" cy="372" rx="26" ry="22" fill="#15803d"/>
  <path d="M528 330 C520 300 540 270 535 245" fill="none" stroke="#047857" stroke-width="3"
    stroke-dasharray="5 5" marker-end="url(#wc-arrow-g)"/>
  <path d="M545 335 C560 305 555 275 570 250" fill="none" stroke="#059669" stroke-width="2.5"
    stroke-dasharray="4 5" marker-end="url(#wc-arrow-g)"/>
  <text x="600" y="290" font-family="Lexend,Arial,sans-serif" font-size="13"
    font-weight="700" fill="#047857">Transpiration</text>
  <text x="600" y="306" font-family="Lexend,Arial,sans-serif" font-size="11"
    fill="#065f46">plants release vapour</text>

  <!-- Cloud + Condensation -->
  <g filter="url(#wc-shadow)">
    <ellipse cx="700" cy="170" rx="90" ry="42" fill="#fff"/>
    <ellipse cx="650" cy="185" rx="55" ry="32" fill="#f8fafc"/>
    <ellipse cx="755" cy="182" rx="60" ry="34" fill="#e2e8f0"/>
    <ellipse cx="700" cy="150" rx="50" ry="28" fill="#fff"/>
  </g>
  <circle cx="670" cy="195" r="3" fill="#38bdf8"/><circle cx="690" cy="200" r="3" fill="#38bdf8"/>
  <circle cx="710" cy="198" r="3" fill="#38bdf8"/><circle cx="730" cy="196" r="3" fill="#38bdf8"/>
  <text x="700" y="130" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="15" font-weight="700" fill="#0B2E59">2. Condensation</text>
  <text x="700" y="238" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="11" fill="#475569">vapour cools → tiny droplets (cloud)</text>

  <!-- Arrow vapour into cloud -->
  <path d="M360 280 C480 220 560 190 620 175" fill="none" stroke="#0B2E59" stroke-width="3"
    marker-end="url(#wc-arrow)"/>

  <!-- Precipitation: rain -->
  <g stroke="#0284c7" stroke-width="2.5" stroke-linecap="round">
    <line x1="660" y1="220" x2="640" y2="290"/><line x1="685" y1="225" x2="668" y2="310"/>
    <line x1="710" y1="222" x2="700" y2="320"/><line x1="735" y1="225" x2="728" y2="305"/>
    <line x1="760" y1="220" x2="755" y2="295"/>
  </g>
  <text x="800" y="280" font-family="Lexend,Arial,sans-serif" font-size="15"
    font-weight="700" fill="#0369a1">3. Precipitation</text>
  <text x="800" y="298" font-family="Lexend,Arial,sans-serif" font-size="11"
    fill="#475569">rain · snow · hail</text>

  <!-- Rain back to collection -->
  <path d="M680 320 C560 380 450 430 380 450" fill="none" stroke="#0B2E59" stroke-width="3.5"
    marker-end="url(#wc-arrow)"/>

  <text x="480" y="568" text-anchor="middle" font-family="Lexend,Arial,sans-serif"
    font-size="13" fill="#334155">Evaporation → Condensation → Precipitation → Collection → (repeat)</text>
</svg>""".strip()


def build_vocabulary_visual_svg(vocab: dict) -> str:
    """Premium deterministic visual for Picture Words."""
    topic = str(vocab.get("topic") or "Lesson Vocabulary")
    extra = " ".join(
        str(r.get("term") or "") for r in (vocab.get("picture_words") or [])[:8]
    )
    if _is_water_cycle_topic(topic, extra):
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
