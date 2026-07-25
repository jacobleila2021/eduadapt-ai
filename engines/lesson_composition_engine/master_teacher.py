"""Master-teacher paragraph craft — educational conversation, not templates.

Phase Omega 2.0: every explanation answers "What would an outstanding teacher say next?"
"""

from __future__ import annotations

import re
from typing import Any, Mapping

from engines.lesson_composition_engine.publisher_style_guide import (
    BANNED_AUTHORING,
    MAX_PARAGRAPH_SENTENCES,
    MAX_SENTENCE_WORDS,
)
from engines.lesson_composition_engine.teaching_rules import ensure_paragraph_quality


def _clip_sentence(text: str, max_words: int = MAX_SENTENCE_WORDS) -> str:
    words = (text or "").strip().split()
    if len(words) <= max_words:
        out = " ".join(words)
    else:
        out = " ".join(words[:max_words]).rstrip(",;:")
    if out and out[-1] not in ".!?":
        out += "."
    return out


def _scrub(text: str) -> str:
    out = text or ""
    low = out.lower()
    for phrase in BANNED_AUTHORING:
        if phrase in low:
            # Drop sentences that carry banned authoring
            kept = []
            for sent in re.split(r"(?<=[.!?])\s+", out):
                if phrase not in sent.lower():
                    kept.append(sent)
            out = " ".join(kept).strip()
            low = out.lower()
    return out


def craft_teaching_paragraph(
    *,
    claim: str,
    topic: str,
    concept: str = "",
    example: str = "",
    prior: str = "",
    analogy: str = "",
    curiosity: str = "",
    profile: str = "standard",
) -> str:
    """Build one teachable paragraph in golden classroom voice (no template scaffold)."""
    from engines.lesson_composition_engine.publisher_author import teach_concept_paragraph
    from engines.lesson_composition_engine.recovery import sanitize_concept_label

    topic_s = (topic or "this lesson").strip()
    name = sanitize_concept_label(concept or topic_s, topic=topic_s)
    claim_s = claim or example or f"{name} is defined clearly in this lesson."
    text = teach_concept_paragraph(name=name, claim=claim_s, topic=topic_s, profile=profile)
    return ensure_paragraph_quality(_scrub(text), idea=name)


def enrich_section_body(
    body: str,
    *,
    topic: str,
    title: str = "",
    claim: str = "",
    example: str = "",
    profile: str = "standard",
) -> str:
    """If a section body is thin or template-like, rewrite as master-teacher prose.

    Never destroy already-composed Teacher Composition Framework writing.
    """
    from engines.lesson_composition_engine.recovery import sanitize_concept_label

    text = _scrub(body or "")
    words = text.split()
    low = text.lower()
    # Count real sentence endings — questions and exclamations are complete teaching moves
    sentence_ends = len(re.findall(r"[.!?]+", text))
    # Already-composed educational writing: keep it (Teacher Composition / publisher author)
    composed_markers = (
        "find a living moment",
        "connect it to this accurate meaning",
        "in plain language",
        "many learners believe",
        "what should stay with you",
        "two scenes — one steady",
        "have you noticed",
        "have you seen something like this",
        "why does",
        "follow ",
        "watch carefully",
    )
    if any(m in low for m in composed_markers) and sentence_ends >= 1 and len(words) >= 12:
        return ensure_paragraph_quality(text, idea=title or topic)

    needs = (
        len(words) < 18
        or any(p in low for p in BANNED_AUTHORING)
        or sentence_ends < 1
        or (bool(words) and words[0].lower() == "explain" and len(words) < 40)
    )
    if not needs and len(words) <= 220:
        return ensure_paragraph_quality(text, idea=title or topic)
    concept = sanitize_concept_label(
        title.split("—")[-1].split(":")[-1].strip() if title else topic,
        topic=topic,
    )
    return craft_teaching_paragraph(
        claim=claim or text,
        topic=topic,
        concept=concept,
        example=example,
        profile=profile,
    )


def apply_master_teacher_pass(
    adaptation: dict[str, Any],
    *,
    version_id: str = "standard",
    board: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    from engines.lesson_composition_engine.recovery import (
        clarity_edit_adaptation,
        educational_meaning_preserved,
    )

    board = board or {}
    topic = str(adaptation.get("topic") or board.get("topic") or "Lesson")
    lce = adaptation.get("lce") if isinstance(adaptation.get("lce"), dict) else {}
    # Teacher Composition Framework already authored this lesson — polish clarity only.
    if lce.get("teacher_composition") or lce.get("no_template_banks"):
        out = clarity_edit_adaptation(dict(adaptation), topic=topic)
        out.setdefault("lce", {})
        if isinstance(out["lce"], dict):
            out["lce"]["master_teacher"] = False
            out["lce"]["master_teacher_skipped"] = "teacher_composition_preserved"
        return out

    claims = list(board.get("verified_claims") or [])
    examples = list(board.get("examples") or [])
    out = dict(adaptation)
    sections = []
    for i, sec in enumerate(out.get("sections") or []):
        if not isinstance(sec, dict):
            continue
        row = dict(sec)
        role = str(row.get("role") or "")
        body0 = str(row.get("body") or "")
        if body0.lstrip().startswith("-"):
            sections.append(row)
            continue
        if role in {"visual", "summary", "revision", "hook", "reflection"} and len(body0.split()) > 12:
            # Preserve hooks / reflections / diagrams authored upstream
            sections.append(row)
            continue
        claim = claims[min(i, len(claims) - 1)] if claims else ""
        example = examples[min(i, len(examples) - 1)] if examples else ""
        if isinstance(claim, dict):
            claim = str(claim.get("text") or claim.get("claim") or claim.get("name") or "")
        else:
            claim = str(claim or "")
        if isinstance(example, dict):
            example = str(example.get("text") or example.get("example") or example.get("caption") or "")
        else:
            example = str(example or "")
        row["body"] = enrich_section_body(
            body0,
            topic=topic,
            title=str(row.get("title") or ""),
            claim=claim,
            example=example,
            profile=version_id,
        )
        sections.append(row)
    out["sections"] = sections
    if out.get("big_idea"):
        claim0 = claims[0] if claims else str(out["big_idea"])
        example0 = examples[0] if examples else ""
        if isinstance(claim0, dict):
            claim0 = str(claim0.get("text") or claim0.get("claim") or claim0.get("name") or "")
        else:
            claim0 = str(claim0 or "")
        if isinstance(example0, dict):
            example0 = str(example0.get("text") or example0.get("example") or example0.get("caption") or "")
        else:
            example0 = str(example0 or "")
        # Never pass title="opening" — that polluted Water Cycle with nonsense.
        out["big_idea"] = enrich_section_body(
            str(out["big_idea"]),
            topic=topic,
            title=topic,
            claim=claim0,
            example=example0,
            profile=version_id,
        )
    out = clarity_edit_adaptation(out, topic=topic)
    if not educational_meaning_preserved(adaptation, out):
        # Fall back to clarity scrub of original only
        return clarity_edit_adaptation(dict(adaptation), topic=topic)
    out.setdefault("lce", {})
    if isinstance(out["lce"], dict):
        out["lce"]["master_teacher"] = True
    return out
