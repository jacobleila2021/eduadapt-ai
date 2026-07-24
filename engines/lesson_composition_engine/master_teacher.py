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
    from engines.lesson_composition_engine.recovery import sanitize_concept_label

    topic_s = (topic or "this lesson").strip()
    name = sanitize_concept_label(concept or topic_s, topic=topic_s)
    claim_s = _clip_sentence(claim or f"{name} is defined clearly in this lesson.")
    curiosity_s = _clip_sentence(
        curiosity
        or f"Have you ever wondered why {name.lower()} matters when you study {topic_s}?"
    )
    prior_s = _clip_sentence(
        prior
        or f"You already know everyday patterns that prepare you to understand {name.lower()}."
    )
    analogy_s = _clip_sentence(
        analogy
        or (
            f"Think of {name.lower()} like a familiar idea: once you can say what it does, "
            f"the rest of {topic_s} becomes easier to explain."
        )
    )
    example_s = _clip_sentence(
        example
        or f"In real life, {name.lower()} shows up clearly when you connect it to {topic_s}."
    )
    transition_s = _clip_sentence(
        f"Next, keep this meaning of {name.lower()} in mind as we move one step further."
    )

    if profile == "adhd":
        parts = [
            _clip_sentence(f"Mission for {name}: learn it in one short burst."),
            claim_s,
            _clip_sentence(f"Quick win example: {example_s.rstrip('.')}."),
            _clip_sentence("Pause. Check. Next chunk."),
        ]
    elif profile == "dyslexia":
        parts = [
            _clip_sentence(f"{name}."),
            claim_s,
            _clip_sentence("Read once slowly. Circle the key word."),
            _clip_sentence(f"Whisper the meaning of {name.lower()} once."),
        ]
    elif profile == "ld":
        parts = [
            _clip_sentence(f"Step for {name}:"),
            claim_s,
            _clip_sentence(f"Show you know: {example_s}"),
        ]
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
    elif profile == "visual":
        parts = [
            _clip_sentence(f"Look for {name.lower()} on the diagram before you read."),
            claim_s,
            _clip_sentence(f"Match the picture labels to this example: {example_s}"),
            _clip_sentence(f"Point to the part that shows {name.lower()}, then explain it."),
        ]
    elif profile == "auditory":
        parts = [
            _clip_sentence(f"Listen carefully to {name.lower()}."),
            claim_s,
            _clip_sentence(f"Say it aloud: {claim_s}"),
            _clip_sentence(f"Story cue to remember: {example_s}"),
        ]
    elif profile == "teacher":
        parts = [
            _clip_sentence(f"Model {name} with verified evidence on the board."),
            claim_s,
            _clip_sentence(f"Listen for misconceptions; accept answers that use: {example_s}"),
            _clip_sentence("Exit check: one accurate sentence plus one real example."),
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
    from engines.lesson_composition_engine.recovery import sanitize_concept_label

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
