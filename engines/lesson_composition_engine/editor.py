"""LCE Educational Editor — constrained narrative polish (optional LLM).

Default path is deterministic CLG composition. LLM polish may only rewrite,
simplify, expand, sequence, differentiate, explain, or personalize CLG content.
It must never invent curriculum.
"""

from __future__ import annotations

from typing import Any, Mapping

EDITOR_SYSTEM_CONTRACT = """
You are an Educational Editor for Alora AI — not a curriculum author.

You may ONLY: rewrite, simplify, expand, sequence, differentiate, explain, personalize.
You may ONLY use: Canonical Lesson Graph nodes, uploaded claims, SIF knowledge,
curriculum standards already provided, UVIE visual captions, accessibility rules.

FORBIDDEN:
- Inventing facts, examples, formulas, or diagrams
- Teaching metadata (Learning Objectives lists, Grade Level, Time Allocation, Subject labels)
- Frequency-based vocabulary
- "Imagine a diagram" placeholders
- ChatGPT-sounding fluff or repeated paragraphs

Write like a premium NCERT textbook + expert classroom teacher.
""".strip()


def editor_prompt_block(clg: Mapping[str, Any], lens_id: str) -> str:
    """Build a strict editor brief from CLG (for optional LLM polish)."""
    import json

    slim = {
        "topic": clg.get("topic"),
        "subject_key": clg.get("subject_key"),
        "learning_goals": clg.get("learning_goals"),
        "core_concepts": clg.get("core_concepts"),
        "facts": (clg.get("facts") or [])[:12],
        "vocabulary": clg.get("vocabulary"),
        "misconceptions": clg.get("misconceptions"),
        "visual_refs": clg.get("visual_refs"),
        "assessment_outcomes": clg.get("assessment_outcomes"),
        "relationships": clg.get("relationships"),
        "lens": lens_id,
    }
    return (
        EDITOR_SYSTEM_CONTRACT
        + "\n\nCANONICAL_LESSON_GRAPH (authoritative):\n"
        + json.dumps(slim, ensure_ascii=False)[:12000]
    )


def polish_disabled_by_default() -> bool:
    """LCE 1.0 ships deterministic composition; LLM polish is opt-in."""
    import os

    return os.getenv("LCE_LLM_POLISH", "false").strip().lower() not in {
        "1",
        "true",
        "yes",
        "on",
    }
