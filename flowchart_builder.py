"""
Coloured Mermaid flowchart builder — replaces unreliable AI images with
lesson-accurate, labelled flowcharts (Alora navy/teal palette).
"""

from __future__ import annotations

import re
from typing import Any

# Rotating node colour classes for Mermaid classDef
NODE_CLASSES = [
    ("c1", "#e6f7f8", "#0B2E59", "#008C95"),
    ("c2", "#e3f2fd", "#0B2E59", "#008C95"),
    ("c3", "#ecfdf5", "#0B2E59", "#059669"),
    ("c4", "#fffbeb", "#0B2E59", "#d97706"),
    ("c5", "#f3e8ff", "#0B2E59", "#7c3aed"),
    ("c6", "#fce7f3", "#0B2E59", "#db2777"),
]

SKIP_SECTIONS = {
    "introduction",
    "summary",
    "practice",
    "exam focus",
    "check",
    "review",
    "overview",
    "examples",
}


def _mermaid_safe(text: str, max_len: int = 36) -> str:
    """Sanitise text for Mermaid node labels."""
    cleaned = re.sub(r'["\[\](){}|<>#;]', " ", str(text or ""))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if not cleaned:
        return "Concept"
    if len(cleaned) > max_len:
        cleaned = cleaned[: max_len - 1].rstrip() + "…"
    return cleaned


def _class_defs() -> str:
    lines = [
        "classDef hub fill:#0B2E59,color:#ffffff,stroke:#008C95,stroke-width:2px",
        "classDef group fill:#008C95,color:#ffffff,stroke:#0B2E59,stroke-width:2px",
    ]
    for name, fill, text, stroke in NODE_CLASSES:
        lines.append(
            f"classDef {name} fill:{fill},color:{text},stroke:{stroke},stroke-width:2px"
        )
    return "\n  ".join(lines)


def _short_cue(text: str, max_len: int = 42) -> str:
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return ""
    sentence = re.split(r"(?<=[.!?])\s+", text)[0]
    return _mermaid_safe(sentence, max_len)


def build_vocabulary_flowchart(vocab: dict) -> str:
    """Hub flowchart linking topic to vocabulary terms with colour-coded nodes."""
    topic = _mermaid_safe(vocab.get("topic") or "Lesson Vocabulary", 32)
    terms: list[tuple[str, str]] = []

    for row in vocab.get("picture_words") or []:
        term = (row.get("term") or "").strip()
        cue = _short_cue(row.get("draw_this") or row.get("visual") or "")
        if term:
            terms.append((term, cue))

    if len(terms) < 3:
        for word in vocab.get("word_wall") or []:
            term = (word.get("term") or "").strip()
            if term and term not in {t for t, _ in terms}:
                cue = _short_cue(
                    word.get("child_friendly")
                    or word.get("definition")
                    or word.get("visual_description")
                    or ""
                )
                terms.append((term, cue))

    terms = terms[:12]
    if not terms:
        terms = [("Key term 1", ""), ("Key term 2", ""), ("Key term 3", "")]

    lines = [
        "flowchart TD",
        f'  TOP(["{topic}"]):::hub',
        _class_defs(),
    ]
    for index, (term, cue) in enumerate(terms):
        node_id = f"N{index}"
        cls = NODE_CLASSES[index % len(NODE_CLASSES)][0]
        label = _mermaid_safe(term, 28)
        if cue:
            label = f"{label}<br/><small>{cue}</small>"
        lines.append(f'  TOP --> {node_id}["{label}"]:::{cls}')

    return "\n".join(lines)


def build_lesson_flowchart(lesson: dict) -> str:
    """Coloured flowchart from lesson sections — grouped or sequential."""
    from study_diagram_builder import _study_nodes

    topic, nodes = _study_nodes(lesson if isinstance(lesson, dict) else {})
    topic_label = _mermaid_safe(topic, 32)

    if not nodes:
        return (
            "flowchart TD\n"
            f'  A(["{topic_label}"]):::hub\n'
            f"  {_class_defs()}"
        )

    groups: dict[str, list[dict]] = {}
    for node in nodes:
        groups.setdefault(node.get("group") or "Core concepts", []).append(node)

    distinct = [g for g in groups if g != "Core concepts"]
    lines = ["flowchart TD", f'  TOP(["{topic_label}"]):::hub', _class_defs()]

    if len(distinct) >= 2 and len(groups) <= 4:
        for g_index, (group_name, items) in enumerate(sorted(groups.items())):
            gid = f"G{g_index}"
            gcls = "group"
            lines.append(f'  TOP --> {gid}["{_mermaid_safe(group_name, 24)}"]:::{gcls}')
            for i_index, item in enumerate(items[:5]):
                nid = f"G{g_index}N{i_index}"
                cls = NODE_CLASSES[(g_index + i_index) % len(NODE_CLASSES)][0]
                title = _mermaid_safe(item.get("title", ""), 26)
                facts = item.get("labels") or []
                if facts:
                    title = f"{title}<br/><small>{_mermaid_safe(facts[0], 38)}</small>"
                lines.append(f'  {gid} --> {nid}["{title}"]:::{cls}')
    else:
        prev = "TOP"
        for index, node in enumerate(nodes[:10]):
            nid = f"S{index}"
            cls = NODE_CLASSES[index % len(NODE_CLASSES)][0]
            title = _mermaid_safe(node.get("title", ""), 26)
            facts = node.get("labels") or []
            if facts:
                title = f"{title}<br/><small>{_mermaid_safe(facts[0], 38)}</small>"
            lines.append(f'  {prev} --> {nid}["{title}"]:::{cls}')
            prev = nid

    return "\n".join(lines)


def resolve_lesson_concept_flowchart(lesson: dict) -> str:
    """Prefer AI mermaid when valid; otherwise build from lesson content."""
    raw = (lesson.get("mermaid_diagram") or lesson.get("mermaid") or "").strip()
    if raw and _looks_like_mermaid(raw):
        return raw
    return build_lesson_flowchart(lesson)


def resolve_lesson_study_flowchart(lesson: dict) -> str:
    """Study diagram as a detailed section flowchart (always built for consistency)."""
    return build_lesson_flowchart(lesson)


def _looks_like_mermaid(text: str) -> bool:
    lowered = text.lower()
    return any(
        k in lowered
        for k in ("flowchart", "graph ", "mindmap", "sequencediagram", "timeline")
    )


def flowchart_to_text(diagram: str) -> str:
    """Plain-text fallback for Word export."""
    lines = ["Visual flowchart:"]
    for match in re.finditer(r'\["([^"\]]+)"\]', diagram):
        label = re.sub(r"<[^>]+>", " ", match.group(1))
        label = re.sub(r"\s+", " ", label).strip()
        if label:
            lines.append(f"  • {label}")
    return "\n".join(lines) if len(lines) > 1 else "See online flowchart."
