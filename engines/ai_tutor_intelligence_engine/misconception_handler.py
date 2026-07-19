"""Misconception handling — AME-grounded corrective tutoring."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import GroundingPacket, TutorContext


def handle_misconceptions(
    ctx: TutorContext,
    grounding: GroundingPacket,
) -> dict[str, Any]:
    misc = ctx.misconceptions or []
    if not misc:
        return {"ok": True, "active": [], "corrections": [], "note": "No active misconceptions in context"}

    corrections = []
    for m in misc[:5]:
        if not isinstance(m, dict):
            continue
        label = m.get("label") or m.get("misconception_id")
        evidence = m.get("evidence") or ""
        concept_id = m.get("concept_id") or ""
        verified = ""
        for c in grounding.cie_concepts:
            if c.get("concept_id") == concept_id and c.get("definition"):
                verified = c["definition"]
                break
        if not verified and grounding.rag_hits:
            verified = grounding.rag_hits[0].get("text") or ""
        if not verified and grounding.insufficient_evidence:
            corrections.append(
                {
                    "misconception": label,
                    "ok": False,
                    "content": "Cannot correct confidently without verified curriculum evidence.",
                }
            )
            continue
        corrections.append(
            {
                "misconception": label,
                "ok": True,
                "concept_id": concept_id,
                "content": (
                    f"Common mix-up: **{label}**.\n"
                    f"{evidence}\n\n"
                    f"Verified idea from your materials: {verified}\n\n"
                    "Try restating the correct idea in one sentence."
                ),
                "intervention_ids": m.get("intervention_ids") or [],
                "citations": grounding.citations[:5],
            }
        )

    return {
        "ok": True,
        "active": misc[:5],
        "corrections": corrections,
        "policy": "correct_with_verified_content_only",
    }
