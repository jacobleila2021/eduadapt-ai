"""Learner-facing writing, visual, and vocabulary polish."""

from __future__ import annotations

import re
from typing import Any, Mapping

from engines.lesson_composition_engine.publisher_style_guide import (
    BANNED_AUTHORING,
    CREAM,
    style_guide_css,
)
from epp.constants import ROBOTIC_TRANSITIONS, SCAFFOLD_LEAKS
from epp.personas import apply_persona_intent
from engines.lesson_composition_engine.content_fidelity import simplify_vocabulary_page


def _scrub(text: str) -> str:
    out = text or ""
    banned = tuple(dict.fromkeys([*ROBOTIC_TRANSITIONS, *SCAFFOLD_LEAKS, *BANNED_AUTHORING]))
    for phrase in banned:
        if phrase in out.lower():
            kept = []
            for sent in re.split(r"(?<=[.!?])\s+", out):
                if phrase not in sent.lower():
                    kept.append(sent)
            out = " ".join(kept).strip()
    out = re.sub(r"\s{2,}", " ", out).strip()
    out = re.sub(r"(?i)\bpicture:\s*", "Draw this: ", out)
    out = re.sub(r"(?i)\bmemory tip:\s*", "Remember: ", out)
    return out


def _polish_vocabulary(page: dict[str, Any], *, topic: str) -> dict[str, Any]:
    wall = list(page.get("word_wall") or page.get("vocabulary_cards") or [])
    for row in wall:
        if not isinstance(row, dict):
            continue
        tip = str(row.get("memory_tip") or "")
        low = tip.lower()
        if not tip or "picture" in low or "memory tip" in low:
            term = str(row.get("term") or "this word").strip()
            row["memory_tip"] = (
                f"Draw {term} from the {topic} diagram, then say the meaning in one breath."
            )
        if row.get("example") and not row.get("example_sentence"):
            row["example_sentence"] = row["example"]
        row.setdefault("pmes_flashcard", True)
        row.setdefault("lce_card", True)
        term = str(row.get("term") or "").strip()
        if term and len(term) <= 24:
            row["term"] = term.upper()
    page["word_wall"] = wall
    page["publisher_style_css"] = style_guide_css()
    page.setdefault("style_guide", {"version": "2.0.0", "background": CREAM})
    return page


def polish_adaptations(
    adaptations: dict[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Final scrub + persona intent. Does not re-run master-teacher (PEEC/PMES already did)."""
    board = board or adaptations.get("_intelligence_board") or {}
    topic = str(board.get("topic") or "Lesson")
    out = dict(adaptations)

    for key, value in list(out.items()):
        if str(key).startswith("_") or not isinstance(value, dict):
            continue
        if key == "vocabulary":
            out[key] = simplify_vocabulary_page(dict(value), topic=topic)
            continue
        if key == "worksheet":
            sheet = dict(value)
            sheet["publisher_style_css"] = style_guide_css()
            sheet.setdefault("style_guide", {"version": "2.0.0", "background": CREAM})
            out[key] = sheet
            continue

        page = dict(value)
        if page.get("big_idea"):
            page["big_idea"] = _scrub(str(page["big_idea"]))
        cleaned = []
        for sec in page.get("sections") or []:
            if not isinstance(sec, dict):
                continue
            row = dict(sec)
            row["body"] = _scrub(str(row.get("body") or ""))
            row["title"] = _scrub(str(row.get("title") or ""))
            if row["body"]:
                cleaned.append(row)
        page["sections"] = cleaned
        page = apply_persona_intent(page, version_id=key, topic=topic)
        page["big_idea"] = _scrub(str(page.get("big_idea") or ""))
        final_sections = []
        for sec in page.get("sections") or []:
            if not isinstance(sec, dict):
                continue
            row = dict(sec)
            row["body"] = _scrub(str(row.get("body") or ""))
            if row["body"]:
                final_sections.append(row)
        page["sections"] = final_sections
        page["publisher_style_css"] = style_guide_css()
        page.setdefault("style_guide", {"version": "2.0.0", "background": CREAM})
        page.setdefault("lce", {})
        if isinstance(page["lce"], dict):
            page["lce"]["epp"] = True
            page["lce"]["phase_omega_ultimate"] = True
        out[key] = page

    return out
