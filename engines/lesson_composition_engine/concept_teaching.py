"""Concept teaching blocks — never skip the eight-step instructional sequence."""

from __future__ import annotations

import re
from typing import Any

from engines.lesson_composition_engine.schemas import CONCEPT_TEACHING_STEPS, ConceptBlock, LessonSection
from engines.lesson_composition_engine.teaching_rules import (
    ensure_paragraph_quality,
    pick_transition,
)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def _excerpt_about(source: str, concept: str, *, fallback: str = "") -> str:
    if not source:
        return fallback
    concept_l = concept.lower()
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", source) if p.strip()]
    for p in paragraphs:
        if concept_l and concept_l in p.lower():
            return ensure_paragraph_quality(p[:500], idea=concept)
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", source) if s.strip()]
    hits = [s for s in sentences if concept_l in s.lower()]
    if hits:
        joined = " ".join(hits[:3])
        return ensure_paragraph_quality(joined, idea=concept)
    if sentences:
        return ensure_paragraph_quality(" ".join(sentences[:2]), idea=concept)
    return fallback


def build_concept_block(
    concept: str,
    *,
    source_text: str = "",
    misconception: str = "",
    worked_example: str = "",
    visual_id: str = "",
    index: int = 0,
) -> ConceptBlock:
    cid = re.sub(r"[^a-z0-9]+", "_", concept.lower()).strip("_") or f"concept_{index}"
    explain = _excerpt_about(
        source_text,
        concept,
        fallback=(
            f"{concept} is a core idea in this lesson. "
            f"We will build understanding step by step, starting from familiar experience "
            f"and moving toward precise classroom language."
        ),
    )
    example = (
        f"In everyday life, you can notice {concept.lower()} when you observe how things "
        f"work around you — at home, in the playground, or in a simple classroom demo. "
        f"Connecting the idea to a real situation makes the definition easier to remember."
    )
    worked = worked_example or (
        f"Worked example: Identify where {concept.lower()} appears in the lesson context, "
        f"name the key parts, and explain the idea in two clear sentences using the lesson vocabulary."
    )
    misc = misconception or (
        f"A common mistake is to confuse {concept.lower()} with a related term. "
        f"Keep the definitions separate and check against the lesson explanation."
    )
    practice = (
        f"Practice: In your own words, explain {concept} and give one example from the lesson."
    )
    reflection = (
        f"Reflection: What part of {concept.lower()} feels clear, and what still needs another example?"
    )
    return ConceptBlock(
        concept_id=cid,
        title=concept,
        simple_explanation=explain,
        real_life_example=ensure_paragraph_quality(example, idea=concept),
        visual_id=visual_id,
        worked_example=ensure_paragraph_quality(worked, idea=concept),
        misconception=ensure_paragraph_quality(misc, idea=concept),
        practice_question=practice,
        reflection=reflection,
        body_paragraphs=[explain, example],
    )


def concept_blocks_to_sections(blocks: list[ConceptBlock]) -> list[LessonSection]:
    """Expand concept blocks into ordered lesson sections — no skipped steps."""
    sections: list[LessonSection] = []
    step_index = 0
    for block in blocks:
        mapping = {
            "concept": (
                f"Concept: {block.title}",
                (
                    f"{block.title} sits at the heart of today's learning. "
                    f"Hold this idea in mind as we move from a simple explanation "
                    f"to examples, visuals, and practice."
                ),
            ),
            "simple_explanation": (f"Understanding {block.title}", block.simple_explanation),
            "real_life_example": (f"{block.title} in Everyday Life", block.real_life_example),
            "visual": (
                f"See {block.title}",
                (
                    f"Study the diagram that follows this explanation. "
                    f"Use it to check that each part of {block.title.lower()} is clear before you continue."
                ),
            ),
            "worked_example": (f"Worked Example — {block.title}", block.worked_example),
            "common_misconception": (f"Watch Out — {block.title}", block.misconception),
            "practice_question": (f"Try This — {block.title}", block.practice_question),
            "reflection": (f"Reflect on {block.title}", block.reflection),
        }
        for step in CONCEPT_TEACHING_STEPS:
            title, body = mapping[step]
            sid = f"{block.concept_id}__{step}"
            section = LessonSection(
                section_id=sid,
                title=title,
                role=step,
                body=ensure_paragraph_quality(body, idea=block.title),
                paragraphs=[ensure_paragraph_quality(body, idea=block.title)],
                box="teach" if step in {"concept", "simple_explanation"} else "",
                visual_ids=[block.visual_id] if step == "visual" and block.visual_id else [],
                concept_id=block.concept_id,
                transition_in=pick_transition(step_index),
            )
            sections.append(section)
            step_index += 1
    return sections


def extract_concepts_from_inputs(
    *,
    profile: dict[str, Any] | None = None,
    uli_accessors: dict[str, Any] | None = None,
    sif_analysis: dict[str, Any] | None = None,
    lesson_text: str = "",
) -> list[str]:
    concepts: list[str] = []
    profile = profile or {}
    uli_accessors = uli_accessors or {}
    sif_analysis = sif_analysis or {}

    for key in ("concepts", "key_concepts"):
        for item in profile.get(key) or []:
            if isinstance(item, dict):
                title = item.get("title") or item.get("name") or item.get("concept")
            else:
                title = item
            if title and str(title) not in concepts:
                concepts.append(str(title).strip())

    learning = uli_accessors.get("learning_structure") or {}
    for item in learning.get("key_concepts") or []:
        title = item.get("title") if isinstance(item, dict) else item
        if title and str(title) not in concepts:
            concepts.append(str(title).strip())

    for item in (sif_analysis.get("concepts") or sif_analysis.get("key_concepts") or []):
        title = item.get("title") if isinstance(item, dict) else item
        if title and str(title) not in concepts:
            concepts.append(str(title).strip())

    graph = sif_analysis.get("concept_graph") or {}
    for item in graph.get("nodes") or []:
        if isinstance(item, dict):
            title = item.get("label") or item.get("title") or item.get("id")
            if title and str(title) not in concepts:
                concepts.append(str(title).strip())

    if not concepts and lesson_text:
        # Lightweight noun-ish headings / bold terms
        for m in re.findall(r"^#+\s+(.+)$", lesson_text, flags=re.M):
            t = _clean(m)
            if 3 < len(t) < 60 and t not in concepts:
                concepts.append(t)
            if len(concepts) >= 4:
                break
    return concepts[:8]
