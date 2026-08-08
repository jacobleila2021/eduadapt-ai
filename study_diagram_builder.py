"""
Labelled Study Diagram SVG builder — complete sentences only.

Prefer curriculum flowcharts / Lesson Wall ideas. Never publish mid-phrase OCR scraps.
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
    "home explanation",
    "conversation starters",
    "home activities",
    "parent encouragement",
    "family study plan",
    "parent toolkit",
    "what success looks like at home",
    "common mistakes to avoid",
    "exam practice",
    "practice questions",
}

SKIP_ROLES = {
    "parent_support",
    "teacher_support",
    "practice_question",
    "exam_question",
    "hots_question",
    "assessment",
    "exit_ticket",
    "concept_primer",
    "common_misconception",
}

PANEL_FILLS = [LIGHT_TEAL, LIGHT_BLUE, LIGHT_GREEN, LIGHT_AMBER]


def _wrap_label(text: str, max_len: int = 28) -> list[str]:
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
    return lines[:6]


def _lesson_topic(lesson: dict) -> str:
    from engines.lesson_composition_engine.complete_sentences import strip_adaptation_suffix
    from engines.lesson_composition_engine.vocab_quality import clean_topic

    for key in ("topic", "title"):
        value = strip_adaptation_suffix(str(lesson.get(key) or ""))
        if value and value.lower() not in {"lesson", "lesson topic", "topic", "key ideas"}:
            return clean_topic(value, fallback=value)
    header = lesson.get("header") if isinstance(lesson.get("header"), dict) else {}
    header_topic = strip_adaptation_suffix(str(header.get("topic") or ""))
    if header_topic and header_topic.lower() not in {"lesson", "lesson topic"}:
        return clean_topic(header_topic, fallback=header_topic)
    blob = " ".join(
        str(s.get("title") or "") for s in (lesson.get("sections") or []) if isinstance(s, dict)
    ).lower()
    if any(k in blob for k in ("water cycle", "evaporat", "precipitat")):
        return "The Water Cycle"
    if any(k in blob for k in ("magnetic", "magnetism", "solenoid", "electromagnet")):
        return "Magnetic Effects of Electric Current"
    if any(k in blob for k in ("metal", "non-metal", "nonmetal", "malleab")):
        return "Metals and Non-metals"
    if any(k in blob for k in ("acid", "base", "salt")):
        return "Acids, Bases and Salts"
    if any(k in blob for k in ("electric", "ohm", "circuit", "resistance")):
        return "Electricity"
    return "Key ideas"


def _complete_labels_from_text(body: str, title: str, *, max_labels: int = 2) -> list[str]:
    """Only full sentences — never mid-phrase truncations."""
    from engines.lesson_composition_engine.complete_sentences import (
        ensure_complete_teaching_sentence,
        is_complete_teaching_sentence,
    )

    text = re.sub(r"\s+", " ", (body or "").strip())
    labels: list[str] = []
    for sent in re.split(r"(?<=[.!?])\s+", text):
        fixed = ensure_complete_teaching_sentence(sent)
        if fixed and is_complete_teaching_sentence(fixed) and fixed not in labels:
            labels.append(fixed)
        if len(labels) >= max_labels:
            break
    if labels:
        return labels
    # List phrases → one complete sentence (never bare truncated tokens).
    list_match = re.search(
        r"(?i)(?:including|includes|such as|like|examples?(?: are)?|types?(?: are)?|"
        r"divided into|classified as)[:\s]+(.+?)(?:\.|;|$)",
        text,
    )
    if list_match:
        chunk = list_match.group(1).strip(" .:-")
        fixed = ensure_complete_teaching_sentence(
            f"{title} includes {chunk}."
        )
        if fixed:
            return [fixed]
    title_sent = ensure_complete_teaching_sentence(
        f"{title} is one of the main ideas in this lesson."
    )
    return [title_sent] if title_sent else []


def _extract_fact_labels(body: str, title: str, max_labels: int = 3) -> list[str]:
    """Compatibility wrapper — complete sentences only."""
    return _complete_labels_from_text(body, title, max_labels=max_labels)


def _curriculum_flowchart(topic: str) -> str:
    from engines.lesson_composition_engine.diagrams import build_educational_flowchart_svg
    from engines.lesson_composition_engine.vocab_quality import filter_diagram_stages

    stages = filter_diagram_stages([], topic=topic, limit=6)
    if len(stages) < 3:
        return ""
    return build_educational_flowchart_svg(
        topic,
        stages,
        subtitle="Key ideas in order",
    )


def _wall_flowchart(lesson: dict, topic: str) -> str:
    from engines.lesson_composition_engine.complete_sentences import (
        ensure_complete_teaching_sentence,
    )
    from engines.lesson_composition_engine.diagrams import build_educational_flowchart_svg
    from engines.lesson_composition_engine.vocab_quality import filter_diagram_stages

    wall = lesson.get("lesson_wall") if isinstance(lesson.get("lesson_wall"), list) else []
    titles: list[str] = []
    for row in wall:
        if not isinstance(row, dict):
            continue
        title = str(row.get("title") or "").strip()
        idea = ensure_complete_teaching_sentence(str(row.get("idea") or ""))
        if title and idea:
            titles.append(title)
    stages = filter_diagram_stages(titles, topic=topic, limit=6)
    if len(stages) < 2:
        return ""
    return build_educational_flowchart_svg(
        topic,
        stages,
        subtitle="Key ideas from the Lesson Wall",
    )


def _study_nodes(lesson: dict) -> tuple[str, list[dict]]:
    topic = _lesson_topic(lesson)
    nodes: list[dict] = []
    for section in lesson.get("sections") or []:
        if not isinstance(section, dict):
            continue
        role = str(section.get("role") or "").lower()
        if role in SKIP_ROLES or role.endswith("_support"):
            continue
        title = (section.get("title") or "").strip()
        if not title or title.lower() in SKIP_SECTIONS:
            continue
        if any(k in title.lower() for k in SKIP_SECTIONS):
            continue
        body = (section.get("body") or section.get("content") or "").strip()
        from section_titles import normalize_section_title

        display_title = normalize_section_title(title, body, len(nodes))
        labels = _complete_labels_from_text(body, display_title)
        if not labels:
            continue
        nodes.append(
            {
                "title": display_title,
                "group": "Core concepts",
                "labels": labels,
            }
        )
    # Prefer Lesson Wall complete ideas when sections are thin/OCR.
    if len(nodes) < 3:
        from engines.lesson_composition_engine.complete_sentences import (
            ensure_complete_teaching_sentence,
        )

        for row in lesson.get("lesson_wall") or []:
            if not isinstance(row, dict):
                continue
            title = str(row.get("title") or "").strip()
            idea = ensure_complete_teaching_sentence(str(row.get("idea") or ""))
            if not title or not idea:
                continue
            nodes.append({"title": title, "group": "Core concepts", "labels": [idea]})
            if len(nodes) >= 8:
                break
    return topic, nodes[:8]


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
    title_lines = _wrap_label(title, 22)
    ty = y + 22
    for line in title_lines[:2]:
        parts.append(
            f'<text x="{x + w / 2:.1f}" y="{ty:.1f}" text-anchor="middle" '
            f'font-family="{FONT}" font-size="13" font-weight="700" fill="{NAVY}">'
            f"{html.escape(line)}</text>"
        )
        ty += 18
    ly = ty + 4
    for label in labels[:2]:
        for sub in _wrap_label(label, 34):
            parts.append(
                f'<text x="{x + 12:.1f}" y="{ly:.1f}" font-family="{FONT}" '
                f'font-size="11" fill="#334155">{html.escape(sub)}</text>'
            )
            ly += 14
            if ly > y + h - 8:
                return


def _build_grid_svg(topic: str, nodes: list[dict]) -> str:
    """Labelled grid — each card holds a complete teaching sentence."""
    width = 960
    columns = 2 if len(nodes) <= 4 else 3
    rows = math.ceil(len(nodes) / columns) if nodes else 1
    panel_w = (width - 60) / columns
    panel_h = 168
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
    width = 720
    panel_h = 120
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
    """Build a labelled study diagram — complete sentences / curriculum stages only."""
    data = lesson if isinstance(lesson, dict) else {}
    topic = _lesson_topic(data)

    # Prefer an already-composed domain SVG when it has no ellipsis scraps.
    for field in ("flowchart_svg", "concept_map_svg", "svg_diagram"):
        svg = str(data.get(field) or "")
        if svg.startswith("<svg") and "…" not in svg and "..." not in svg:
            low = svg.lower()
            if "lesson — ld" in low or "lesson — parent" in low:
                continue
            return svg

    # Water cycle: pictorial closed loop before a vertical stage stack.
    if any(k in topic.lower() for k in ("water cycle", "evaporat", "condens", "precipitat")):
        from flowchart_builder import _water_cycle_visual_svg

        return _water_cycle_visual_svg(topic)

    curriculum = _curriculum_flowchart(topic)
    if curriculum:
        return curriculum

    wall_flow = _wall_flowchart(data, topic)
    if wall_flow:
        return wall_flow

    topic, nodes = _study_nodes(data)
    if not nodes:
        curriculum = _curriculum_flowchart(topic)
        if curriculum:
            return curriculum
        from engines.lesson_composition_engine.diagrams import build_educational_flowchart_svg

        return build_educational_flowchart_svg(
            topic,
            ["Key idea", "Example", "Practice"],
            subtitle="Study pathway",
        )

    if _is_process_lesson(topic, nodes) and len(nodes) >= 3:
        return _build_flow_svg(topic, nodes)
    return _build_grid_svg(topic, nodes)


def resolve_study_diagram_svg(lesson: dict) -> str:
    """Use the deterministic, sanitised builder; never inject model-authored SVG."""
    return build_study_diagram_svg(lesson)
