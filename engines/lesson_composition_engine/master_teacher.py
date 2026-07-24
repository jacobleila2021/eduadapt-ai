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
    """Build one teachable paragraph with curiosity → understanding → life → transition."""
    name = (concept or topic or "this idea").strip()
    claim_s = _clip_sentence(claim or f"{name} is defined clearly in this lesson.")
    curiosity_s = _clip_sentence(
        curiosity
        or f"Have you ever wondered why {name.lower()} matters when you look at {topic}?"
    )
    prior_s = _clip_sentence(
        prior
        or f"You already know everyday pushes, pulls, or patterns that prepare you for {name.lower()}."
    )
    analogy_s = _clip_sentence(
        analogy
        or (
            f"Think of {name.lower()} like a familiar tool: once you name what it does, "
            f"the rest of {topic} becomes easier to explain."
        )
    )
    example_s = _clip_sentence(
        example
        or f"In real life, {name.lower()} shows up clearly when you connect it to {topic}."
    )
    transition_s = _clip_sentence(
        f"Next, keep this meaning of {name.lower()} in mind as we move one step further."
    )

    if profile in {"adhd", "dyslexia", "ld"}:
        parts = [curiosity_s, claim_s, example_s]
    elif profile == "autism":
        parts = [
            _clip_sentence(f"First, the idea is {name}."),
            claim_s,
            example_s,
            _clip_sentence("Next comes the example check."),
        ]
    elif profile == "ell":
        parts = [
            _clip_sentence(f"New word focus: {name}."),
            claim_s,
            example_s,
            _clip_sentence(f"Say: “{name} means…” in one short sentence."),
        ]
    elif profile == "parent":
        parts = [
            _clip_sentence(f"At home, ask what {name.lower()} means."),
            claim_s,
            example_s,
        ]
    else:
        parts = [curiosity_s, prior_s, claim_s, analogy_s, example_s, transition_s]

    # Keep rhythm within style-guide sentence budget
    parts = [p for p in parts if p][: MAX_PARAGRAPH_SENTENCES + 2]
    text = _scrub(" ".join(parts))
    return ensure_paragraph_quality(text, idea=name)


def enrich_section_body(
    body: str,
    *,
    topic: str,
    title: str = "",
    claim: str = "",
    example: str = "",
    profile: str = "standard",
) -> str:
    """If a section body is thin or template-like, rewrite as master-teacher prose."""
    text = _scrub(body or "")
    words = text.split()
    low = text.lower()
    needs = (
        len(words) < 28
        or any(p in low for p in BANNED_AUTHORING)
        or text.count(".") < 2
        or (bool(words) and words[0].lower() == "explain")
    )
    if not needs and len(words) <= 160:
        return ensure_paragraph_quality(text, idea=title or topic)
    concept = title.split("—")[-1].split(":")[-1].strip() if title else topic
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
    board = board or {}
    topic = str(adaptation.get("topic") or board.get("topic") or "Lesson")
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
        if role in {"visual", "summary", "revision"} and len(body0.split()) > 20:
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
        out["big_idea"] = enrich_section_body(
            str(out["big_idea"]),
            topic=topic,
            title="opening",
            claim=claim0,
            example=example0,
            profile=version_id,
        )
    out.setdefault("lce", {})
    if isinstance(out["lce"], dict):
        out["lce"]["master_teacher"] = True
    return out
