"""Graduated hint ladder — prefer hints over answers; never invent keys."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import GroundingPacket, HINT_LEVELS, TutorContext


def generate_hint(
    ctx: TutorContext,
    grounding: GroundingPacket,
    *,
    level: int = 1,
    allow_full_solution: bool = False,
) -> dict[str, Any]:
    if grounding.insufficient_evidence or not grounding.ok:
        return {
            "ok": False,
            "level": level,
            "content": grounding.reason,
            "policy": "refuse_without_grounding",
        }

    level = max(1, min(5, int(level)))
    if level == 5 and not allow_full_solution and not ctx.allow_direct_answers:
        level = 4

    title = ctx.topic or (
        grounding.cie_concepts[0].get("title") if grounding.cie_concepts else "the concept"
    )
    evidence = (grounding.rag_hits[0].get("text") if grounding.rag_hits else "") or ""
    definition = ""
    if grounding.cie_concepts:
        definition = grounding.cie_concepts[0].get("definition") or ""

    ladder = {
        1: f"Hint 1 — Prompt thinking: What do you already know about **{title}**? "
        f"Which words in the question connect to your lesson?",
        2: f"Hint 2 — Guide reasoning: Focus on the key idea of **{title}**. "
        f"What relationship or definition should you recall first?",
        3: f"Hint 3 — Partial solution: A verified idea from your materials is: "
        f"{(definition or evidence)[:220]}{'…' if len(definition or evidence) > 220 else ''}",
        4: f"Hint 4 — Nearly complete: Use this verified statement and finish the last step yourself: "
        f"{(definition or evidence)[:320]}",
        5: f"Hint 5 — Full worked solution (verified sources only):\n"
        f"{definition or evidence}\n"
        f"Citations: {', '.join(grounding.citations[:5]) or 'see lesson'}",
    }

    return {
        "ok": True,
        "level": level,
        "levels_available": list(HINT_LEVELS),
        "content": ladder[level],
        "citations": grounding.citations[:8],
        "prefer_hints_over_answers": True,
        "policy": "no_invented_answer_keys",
    }
