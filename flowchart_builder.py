"""
Coloured Mermaid flowchart builder — replaces unreliable AI images with
lesson-accurate, labelled flowcharts (Alora navy/teal palette).

Uses Mermaid 10-safe syntax only (no HTML labels, no invalid node shapes).
"""

from __future__ import annotations

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
    """Prefer sanitised AI mermaid; fall back to built flowchart on parse risk."""
    raw = (lesson.get("mermaid_diagram") or lesson.get("mermaid") or "").strip()
    if raw and _ai_mermaid_is_safe(raw):
        return raw
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
