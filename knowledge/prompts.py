"""RAG citation rules and prompt blocks for the Teaching Layer."""

from __future__ import annotations

from knowledge.types import OfficialMcq, RagHit

RAG_RULES = """
KNOWLEDGE LAYER — RETRIEVED SOURCES (mandatory when provided):
- Use RETRIEVED_SOURCES for curriculum facts, definitions, and processes.
- NEVER contradict retrieved NCERT / Exemplar / CBSE content.
- Cite every major curriculum claim inline using the provided citation tags, e.g. [NCERT Class 8 Science Ch.5 p.62].
- If a fact is not in RETRIEVED_SOURCES or the lesson excerpt, write NEED_SOURCE:{topic} instead of inventing.
- Official MCQ answers in OFFICIAL_ANSWER_BANK must be copied exactly — never change the keyed answer letter or value.
"""


def rag_hits_to_prompt_block(hits: list[RagHit]) -> str:
    if not hits:
        return ""
    lines = ["RETRIEVED_SOURCES (cite these in explanations):"]
    for i, hit in enumerate(hits, start=1):
        lines.append(f"{i}. {hit.citation} — {hit.chapter_title}")
        lines.append(f"   {hit.text[:900]}")
    return "\n".join(lines)


def official_bank_to_prompt_block(items: list[OfficialMcq]) -> str:
    if not items:
        return ""
    lines = ["OFFICIAL_ANSWER_BANK (use exact official_answer — do NOT invent keys):"]
    for i, item in enumerate(items, start=1):
        lines.append(f"{i}. {item.item_id} | {item.source} | Ch.{item.chapter} | {item.topic}")
        lines.append(f"   Q: {item.question}")
        if item.options:
            lines.append(f"   Options: {' | '.join(item.options)}")
        lines.append(f"   official_answer: {item.official_answer}")
        lines.append(f"   explanation: {item.explanation}")
    return "\n".join(lines)
