"""Socratic questioning — grounded prompts, not answer dumps."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import GroundingPacket, TutorContext


def socratic_turn(ctx: TutorContext, grounding: GroundingPacket) -> dict[str, Any]:
    if grounding.insufficient_evidence:
        return {
            "ok": False,
            "questions": [],
            "content": grounding.reason,
        }

    title = ctx.topic or (
        grounding.cie_concepts[0].get("title") if grounding.cie_concepts else "this topic"
    )
    questions = [
        f"In your own words, what is **{title}**?",
        "Which part of the lesson or diagram supports your idea?",
        "What might a common mistake be here — and how would you check it?",
    ]
    if ctx.misconceptions:
        label = ctx.misconceptions[0].get("label") if isinstance(ctx.misconceptions[0], dict) else str(ctx.misconceptions[0])
        questions.append(f"Someone might think: “{label}”. Why is that incomplete according to your materials?")
    if ctx.learning_objectives:
        questions.append(f"How does this help you meet: {ctx.learning_objectives[0]}?")

    return {
        "ok": True,
        "mode": "socratic",
        "questions": questions[:5],
        "content": "Let's think together:\n" + "\n".join(f"{i}. {q}" for i, q in enumerate(questions[:4], 1)),
        "citations": grounding.citations[:6],
        "policy": "questions_only_facts_remain_in_materials",
    }
