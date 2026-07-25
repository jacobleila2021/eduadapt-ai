"""Teaching rules — progressive pedagogy, scaffolding, chunking, storytelling."""

from __future__ import annotations

import re
from typing import Any

from engines.lesson_composition_engine.contracts import subject_sequence
from engines.lesson_composition_engine.schemas import CONCEPT_TEACHING_STEPS

MAX_PARAGRAPH_WORDS = 120
MIN_SENTENCES = 2

# Deprecated: never author learner prose from a fixed transition bank.
# Kept empty so accidental callers cannot inject canned scaffolds.
TRANSITION_BANK: tuple[str, ...] = ()


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def sentence_count(text: str) -> int:
    parts = re.split(r"[.!?]+", (text or "").strip())
    return len([p for p in parts if p.strip()])


def split_paragraphs(text: str) -> list[str]:
    chunks = re.split(r"\n\s*\n", (text or "").strip())
    return [c.strip() for c in chunks if c.strip()]


def ensure_paragraph_quality(paragraph: str, *, idea: str = "") -> str:
    """Normalize teaching prose without injecting meta scaffolding."""
    text = re.sub(r"\s+", " ", (paragraph or "").strip())
    # Strip legacy score-inflation filler if present
    text = re.sub(
        r"(?i)\s*Remember:\s+[^.?!]+helps you explain the topic clearly\.?",
        "",
        text,
    ).strip()
    if not text:
        if idea:
            return f"{idea.rstrip('.')} is defined clearly in this lesson."
        return ""
    # Soft-trim very long paragraphs at sentence boundaries
    words = text.split()
    if len(words) > MAX_PARAGRAPH_WORDS + 40:
        clipped = " ".join(words[:MAX_PARAGRAPH_WORDS])
        if "." in clipped:
            clipped = clipped.rsplit(".", 1)[0] + "."
        text = clipped
    if text and text[-1] not in ".!?":
        text += "."
    return text


def progressive_section_plan(subject: str, concepts: list[str]) -> list[dict[str, Any]]:
    """Build ordered section roles for a subject + concept list."""
    seq = list(subject_sequence(subject))
    plan: list[dict[str, Any]] = [
        {"role": "hook", "title": "Opening the Lesson", "concept": ""},
    ]
    for concept in concepts[:6]:
        for step in CONCEPT_TEACHING_STEPS:
            plan.append(
                {
                    "role": step,
                    "title": _step_title(step, concept),
                    "concept": concept,
                }
            )
    # Subject-flavoured wrap-up always present
    for role, title in (
        ("summary", "Lesson Summary"),
        ("revision", "Quick Revision"),
        ("reflection", "Think About It"),
        ("application", "Apply Your Learning"),
    ):
        if role not in {p["role"] for p in plan[-4:]}:
            plan.append({"role": role, "title": title, "concept": ""})
    # Ensure subject sequence roles appear at least once for MIP/PIP/etc. flavour
    present = {p["role"] for p in plan}
    for role in seq:
        if role not in present and role not in CONCEPT_TEACHING_STEPS:
            plan.insert(
                min(2, len(plan)),
                {"role": role, "title": role.replace("_", " ").title(), "concept": ""},
            )
    return plan


def _step_title(step: str, concept: str) -> str:
    labels = {
        "concept": f"Concept: {concept}",
        "simple_explanation": f"Understanding {concept}",
        "real_life_example": f"{concept} in Everyday Life",
        "visual": f"See {concept}",
        "worked_example": f"Worked Example — {concept}",
        "common_misconception": f"Watch Out — {concept}",
        "practice_question": f"Try This — {concept}",
        "reflection": f"Reflect on {concept}",
    }
    return labels.get(step, f"{step.replace('_', ' ').title()}: {concept}")


def pick_transition(index: int, *, previous: str = "", nxt: str = "", topic: str = "this lesson") -> str:
    """Dynamic teacher transition — never retrieve a canned TRANSITION_BANK line."""
    from engines.lesson_composition_engine.teacher_composition import compose_transition

    prev = previous or (f"idea {index}" if index else "")
    following = nxt or f"the next idea"
    return compose_transition(previous=prev, nxt=following, topic=topic or "this lesson")


def dedupe_sentences(text: str) -> str:
    """Remove exact consecutive sentence duplicates."""
    parts = re.split(r"(?<=[.!?])\s+", (text or "").strip())
    out: list[str] = []
    prev = ""
    for part in parts:
        norm = re.sub(r"\s+", " ", part.strip().lower())
        if not norm or norm == prev:
            continue
        out.append(part.strip())
        prev = norm
    return " ".join(out)


def scaffold_chunk(text: str, *, max_bullets: int = 8) -> list[str]:
    """Chunk prose into short teaching bullets for neurodiversity scaffolds."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if s.strip()]
    return sentences[:max_bullets]
