"""PEEC remediations — polish learner experience without new engines."""

from __future__ import annotations

import re
from typing import Any, Mapping

from engines.lesson_composition_engine.master_teacher import apply_master_teacher_pass
from engines.lesson_composition_engine.publisher_remediation import remediate_adaptation
from engines.lesson_composition_engine.publisher_style_guide import style_guide_css
from peec.constants import MECHANICAL_PHRASES


def _scrub_mechanical(text: str) -> str:
    out = text or ""
    for phrase in MECHANICAL_PHRASES:
        if phrase in out.lower():
            # Drop sentences containing the phrase
            kept = []
            for sent in re.split(r"(?<=[.!?])\s+", out):
                if phrase not in sent.lower():
                    kept.append(sent)
            out = " ".join(kept).strip()
    out = re.sub(r"\s{2,}", " ", out).strip()
    return out


def _ensure_confidence_close(adaptation: dict[str, Any], *, topic: str) -> dict[str, Any]:
    sections = [s for s in (adaptation.get("sections") or []) if isinstance(s, dict)]
    if not sections:
        return adaptation
    roles = {str(s.get("role") or "") for s in sections}
    if "summary" not in roles:
        sections.append(
            {
                "title": "Lesson Summary",
                "role": "summary",
                "box": "summary",
                "body": (
                    f"You can explain the key ideas in {topic} in your own words now. "
                    "Check one example, then take a short pause before you revise."
                ),
            }
        )
    else:
        # Strengthen last summary if it lacks confidence language
        for sec in sections:
            if str(sec.get("role") or "") == "summary":
                body = str(sec.get("body") or "")
                if not any(w in body.lower() for w in ("you can", "ready", "check", "proud")):
                    sec["body"] = (
                        body.rstrip(".")
                        + f". You can check one example from {topic} and feel ready for the next step."
                    )
                break
    adaptation["sections"] = sections
    return adaptation


def _ensure_diagram_purpose(adaptation: dict[str, Any], *, topic: str) -> dict[str, Any]:
    svg = str(
        adaptation.get("flowchart_svg")
        or adaptation.get("svg_diagram")
        or adaptation.get("concept_map_svg")
        or ""
    )
    if not svg.startswith("<svg"):
        return adaptation
    pkg = dict(adaptation.get("diagram_package") or {})
    pkg.setdefault("title", topic)
    pkg.setdefault("caption", f"{topic}: how the key ideas connect")
    pkg.setdefault(
        "explanation",
        f"This diagram is here to make {topic} easier to see and remember. "
        "Trace each label, then match it to the explanation.",
    )
    pkg.setdefault(
        "practice_question",
        f"Point to one part of the diagram and explain it in one clear sentence.",
    )
    pkg.setdefault("callouts", [f"Label: {topic}"])
    pkg["svg"] = svg
    adaptation["diagram_package"] = pkg

    blob = " ".join(
        str(s.get("body") or "") + str(s.get("title") or "")
        for s in (adaptation.get("sections") or [])
        if isinstance(s, dict)
    ).lower()
    if "diagram" not in blob and "see" not in blob:
        sections = list(adaptation.get("sections") or [])
        sections.insert(
            0,
            {
                "title": "Using the Diagram",
                "role": "visual",
                "box": "visual",
                "body": (
                    f"{pkg['explanation']} {pkg['caption']}. "
                    f"Practice: {pkg['practice_question']}"
                ),
            },
        )
        adaptation["sections"] = sections
    return adaptation


def _polish_vocabulary(page: dict[str, Any]) -> dict[str, Any]:
    wall = list(page.get("word_wall") or page.get("vocabulary_cards") or [])
    for row in wall:
        if not isinstance(row, dict):
            continue
        term = str(row.get("term") or "").strip()
        if term and len(term) <= 24:
            row["term"] = term.upper()
        row.setdefault("pmes_flashcard", True)
        row.setdefault("lce_card", True)
        if not row.get("memory_tip"):
            row["memory_tip"] = f"Draw {term} from the lesson diagram, then say what it means."
        if not row.get("example_sentence") and row.get("example"):
            row["example_sentence"] = row["example"]
        if not row.get("pronunciation") and term:
            # Lightweight pronounceable cue — not invented IPA
            row["pronunciation"] = "-".join(term.lower().split()[:3]) or term.lower()
        row.setdefault("audio_label", f"Listen: {term}")
    page["word_wall"] = wall
    page["publisher_style_css"] = style_guide_css()
    return page


def remediate_for_product_excellence(
    adaptations: dict[str, Any],
    *,
    board: Mapping[str, Any] | None = None,
    audit: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Apply experience remediations driven by audit findings."""
    board = board or adaptations.get("_intelligence_board") or {}
    topic = str(board.get("topic") or "Lesson")
    claims = list(board.get("verified_claims") or [])
    out = dict(adaptations)

    for key, value in list(out.items()):
        if key.startswith("_") or not isinstance(value, dict):
            continue
        if key == "vocabulary":
            out[key] = _polish_vocabulary(dict(value))
            continue
        if key == "worksheet":
            sheet = dict(value)
            sheet["publisher_style_css"] = style_guide_css()
            out[key] = sheet
            continue

        page = dict(value)
        # Scrub mechanical language
        if page.get("big_idea"):
            page["big_idea"] = _scrub_mechanical(str(page["big_idea"]))
        new_sections = []
        for sec in page.get("sections") or []:
            if not isinstance(sec, dict):
                continue
            row = dict(sec)
            row["body"] = _scrub_mechanical(str(row.get("body") or ""))
            new_sections.append(row)
        page["sections"] = new_sections

        page = apply_master_teacher_pass(page, version_id=key, board=board)
        page = remediate_adaptation(page, claims=claims)
        page = _ensure_diagram_purpose(page, topic=topic)
        page = _ensure_confidence_close(page, topic=topic)
        page["publisher_style_css"] = style_guide_css()
        page.setdefault("style_guide", {"version": "2.0.0", "background": "#FFF9EE"})
        page.setdefault("lce", {})
        if isinstance(page["lce"], dict):
            page["lce"]["peec"] = True
        out[key] = page

    out["_peec"] = {
        "remediated": True,
        "audit_ref": (audit or {}).get("schema"),
    }
    return out
