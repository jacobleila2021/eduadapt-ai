"""
Labelled Study Diagram SVG builder — lesson-accurate diagrams from section content.
Produces grouped/classification layouts with fact labels extracted from lesson bodies.
"""

from __future__ import annotations

import html
import math
import re
from typing import Any

NAVY = "#0B2E59"
TEAL = "#008C95"
LIGHT_TEAL = "#e6f7f8"
LIGHT_BLUE = "#e3f2fd"
LIGHT_GREEN = "#ecfdf5"
LIGHT_AMBER = "#fffbeb"
FONT = "Lexend, Arial, Verdana, sans-serif"

SKIP_SECTIONS = {
    "introduction",
    "summary",
    "practice",
    "exam focus",
    "check",
    "review",
    "overview",
    "examples",
    "assessment",
}

GROUP_HINTS: list[tuple[str, str]] = [
    ("plant", "Plant"),
    ("animal", "Animal"),
    ("vertebrate", "Vertebrates"),
    ("invertebrate", "Invertebrates"),
    ("xylem", "Transport"),
    ("phloem", "Transport"),
    ("evaporation", "Water cycle"),
    ("condensation", "Water cycle"),
    ("precipitation", "Water cycle"),
    ("solid", "States of matter"),
    ("liquid", "States of matter"),
    ("gas", "States of matter"),
]

PANEL_FILLS = [LIGHT_TEAL, LIGHT_BLUE, LIGHT_GREEN, LIGHT_AMBER]


def _wrap_label(text: str, max_len: int = 22) -> list[str]:
    words = (text or "").split()
    if not words:
        return [""]
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


def _lesson_topic(lesson: dict) -> str:
    for key in ("topic", "title"):
        value = (lesson.get(key) or "").strip()
        if value:
            return value
    big = (lesson.get("big_idea") or "").strip()
    return big[:60] if big else "Lesson Topic"


def _infer_group(title: str, body: str) -> str:
    combined = f"{title} {body[:160]}".lower()
    for keyword, group in GROUP_HINTS:
        if keyword in combined:
            return group
    title_lower = title.lower()
    if any(word in title_lower for word in ("tissue", "cell", "organ")):
        if "plant" in combined:
            return "Plant"
        if "animal" in combined:
            return "Animal"
        return "Structure"
    return "Core concepts"


def _extract_fact_labels(body: str, title: str, max_labels: int = 3) -> list[str]:
    """Pull short, label-worthy facts from section body text."""
    text = re.sub(r"\s+", " ", (body or "").strip())
    if not text:
        return [f"Study: {title}"]

    labels: list[str] = []

    list_match = re.search(
        r"(?:including|includes|such as|like|examples?(?: are)?|types?(?: are)?|"
        r"divided into|classified as)[:\s]+(.+?)(?:\.|;|$)",
        text,
        re.IGNORECASE,
    )
    if list_match:
        chunk = list_match.group(1)
        parts = re.split(r",|\band\b|\bor\b", chunk)
        for part in parts:
            cleaned = part.strip(" .:-")[:48]
            if len(cleaned) > 3:
                labels.append(cleaned)
            if len(labels) >= max_labels:
                break

    if len(labels) < max_labels:
        first_sentence = re.split(r"(?<=[.!?])\s+", text)[0].strip()
        if first_sentence and len(first_sentence) > 12:
            snippet = first_sentence[:55]
            if len(first_sentence) > 55:
                snippet = snippet.rsplit(" ", 1)[0] + "…"
            if snippet not in labels:
                labels.insert(0, snippet)

    if not labels:
        from section_titles import normalize_section_title

        labels.append(normalize_section_title(title, body))

    return labels[:max_labels]


def _study_nodes(lesson: dict) -> tuple[str, list[dict]]:
    topic = _lesson_topic(lesson)
    nodes: list[dict] = []
    for section in lesson.get("sections") or []:
        title = (section.get("title") or "").strip()
        if not title or title.lower() in SKIP_SECTIONS:
            continue
        body = (section.get("body") or section.get("content") or "").strip()
        from section_titles import normalize_section_title

        display_title = normalize_section_title(title, body, len(nodes))
        nodes.append(
            {
                "title": display_title,
                "group": _infer_group(display_title, body),
                "labels": _extract_fact_labels(body, display_title),
            }
        )
    if not nodes:
        for point in lesson.get("key_points") or lesson.get("objectives") or []:
            if isinstance(point, str) and point.strip():
                nodes.append(
                    {
                        "title": point.strip()[:40],
                        "group": "Core concepts",
                        "labels": [point.strip()[:70]],
                    }
                )
    return topic, nodes[:10]


def svg_text_label_count(svg: str) -> int:
    return len(re.findall(r"<text\b", svg or "", re.IGNORECASE))


def _svg_header(title: str, width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="Study diagram for {html.escape(title)}">',
        f'<defs><marker id="study-arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" '
        f'orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="{TEAL}"/></marker></defs>',
        f'<rect width="100%" height="100%" fill="#fafcfd"/>',
        f'<rect x="24" y="16" width="{width - 48}" height="52" rx="12" fill="{NAVY}" '
        f'stroke="{TEAL}" stroke-width="2"/>',
    ] + [
        f'<text x="{width // 2}" y="{38 + i * 18}" text-anchor="middle" font-family="{FONT}" '
        f'font-size="15" font-weight="700" fill="#ffffff">{html.escape(line)}</text>'
        for i, line in enumerate(_wrap_label(title, 42))
    ]


def _draw_panel(
    parts: list[str],
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    labels: list[str],
    fill: str,
) -> None:
    parts.append(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="10" '
        f'fill="{fill}" stroke="{TEAL}" stroke-width="2"/>'
    )
    title_lines = _wrap_label(title, 18)
    ty = y + 22
    for line in title_lines:
        parts.append(
            f'<text x="{x + w / 2:.1f}" y="{ty:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="13" font-weight="700" fill="{NAVY}">'
            f"{html.escape(line)}</text>"
        )
        ty += 18
    ly = ty + 6
    for label in labels:
        for sub in _wrap_label(f"• {label}", 26):
            parts.append(
                f'<text x="{x + 12:.1f}" y="{ly:.1f}" font-family="{FONT}" '
                f'font-size="11" fill="#334155">{html.escape(sub)}</text>'
            )
            ly += 15
            if ly > y + h - 8:
                return


def _build_grouped_svg(topic: str, nodes: list[dict], groups: dict[str, list[dict]]) -> str:
    """Two-or-more-column grouped study diagram (e.g. Plant vs Animal)."""
    width = 920
    group_names = list(groups.keys())[:3]
    col_count = len(group_names)
    col_w = (width - 80) // col_count
    max_items = max(len(groups[g]) for g in group_names)
    panel_h = 118
    header_h = 44
    height = 96 + header_h + max_items * (panel_h + 16) + 40

    parts = _svg_header(topic, width, height)
    top_y = 88

    for col_index, group_name in enumerate(group_names):
        col_x = 40 + col_index * col_w
        parts.append(
            f'<rect x="{col_x + 8:.1f}" y="{top_y:.1f}" width="{col_w - 16:.1f}" '
            f'height="{header_h:.1f}" rx="10" fill="{NAVY}" stroke="{TEAL}" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{col_x + col_w / 2:.1f}" y="{top_y + 28:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="14" font-weight="700" fill="#ffffff">'
            f"{html.escape(group_name)}</text>"
        )
        item_y = top_y + header_h + 14
        for item_index, item in enumerate(groups[group_name]):
            fill = PANEL_FILLS[item_index % len(PANEL_FILLS)]
            _draw_panel(
                parts,
                col_x + 10,
                item_y,
                col_w - 20,
                panel_h,
                item["title"],
                item["labels"],
                fill,
            )
            if item_index == 0:
                parts.append(
                    f'<line x1="{col_x + col_w / 2:.1f}" y1="{top_y + header_h:.1f}" '
                    f'x2="{col_x + col_w / 2:.1f}" y2="{item_y:.1f}" stroke="{TEAL}" '
                    f'stroke-width="2" marker-end="url(#study-arrow)"/>'
                )
            item_y += panel_h + 16

    parts.append("</svg>")
    return "\n".join(parts)


def _build_grid_svg(topic: str, nodes: list[dict]) -> str:
    """Labelled grid — each lesson section as a panel with fact bullets."""
    width = 920
    columns = 3 if len(nodes) > 4 else 2
    rows = math.ceil(len(nodes) / columns)
    panel_w = (width - 60) / columns
    panel_h = 132
    height = 96 + rows * (panel_h + 18) + 24

    parts = _svg_header(topic, width, height)
    start_y = 88

    for index, node in enumerate(nodes):
        row = index // columns
        col = index % columns
        x = 30 + col * panel_w
        y = start_y + row * (panel_h + 18)
        fill = PANEL_FILLS[index % len(PANEL_FILLS)]
        _draw_panel(parts, x, y, panel_w - 12, panel_h, node["title"], node["labels"], fill)

    parts.append("</svg>")
    return "\n".join(parts)


def _build_flow_svg(topic: str, nodes: list[dict]) -> str:
    """Vertical flow when sections follow a process sequence."""
    width = 720
    panel_h = 96
    gap = 22
    height = 96 + len(nodes) * (panel_h + gap) + 20
    cx = width // 2
    panel_w = 560
    px = (width - panel_w) / 2

    parts = _svg_header(topic, width, height)
    y = 88
    for index, node in enumerate(nodes):
        fill = PANEL_FILLS[index % len(PANEL_FILLS)]
        _draw_panel(parts, px, y, panel_w, panel_h, node["title"], node["labels"], fill)
        if index < len(nodes) - 1:
            arrow_y1 = y + panel_h
            arrow_y2 = y + panel_h + gap
            parts.append(
                f'<line x1="{cx}" y1="{arrow_y1}" x2="{cx}" y2="{arrow_y2}" '
                f'stroke="{TEAL}" stroke-width="2" marker-end="url(#study-arrow)"/>'
            )
        y += panel_h + gap

    parts.append("</svg>")
    return "\n".join(parts)


def _is_process_lesson(topic: str, nodes: list[dict]) -> bool:
    combined = topic.lower() + " ".join(n["title"].lower() for n in nodes)
    process_words = ("cycle", "process", "stage", "step", "phase", "flow", "sequence")
    return any(word in combined for word in process_words)


def build_study_diagram_svg(lesson: Any) -> str:
    """Build a labelled, lesson-specific study diagram SVG from section content."""
    data = lesson if isinstance(lesson, dict) else {}
    topic, nodes = _study_nodes(data)
    if "water cycle" in topic.lower():
        from flowchart_builder import _water_cycle_visual_svg

        return _water_cycle_visual_svg(topic)
    if not nodes:
        from concept_map_builder import build_vocabulary_concept_map_svg

        return build_vocabulary_concept_map_svg(
            {"topic": topic, "word_wall": [{"term": "Key idea 1"}, {"term": "Key idea 2"}]}
        )

    groups: dict[str, list[dict]] = {}
    for node in nodes:
        groups.setdefault(node["group"], []).append(node)

    distinct_groups = [g for g in groups if g != "Core concepts"]
    if len(distinct_groups) >= 2 and len(groups) <= 4:
        ordered = sorted(groups.items(), key=lambda item: item[0])
        return _build_grouped_svg(topic, nodes, dict(ordered))

    if _is_process_lesson(topic, nodes) and len(nodes) >= 3:
        return _build_flow_svg(topic, nodes)

    return _build_grid_svg(topic, nodes)


def resolve_study_diagram_svg(lesson: dict) -> str:
    """Use the deterministic, sanitised builder; never inject model-authored SVG."""
    return build_study_diagram_svg(lesson)
