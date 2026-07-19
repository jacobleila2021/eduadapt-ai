"""Worked examples — structure from verified STEM/CIE; no invented math."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import GroundingPacket, TutorContext


def worked_example(ctx: TutorContext, grounding: GroundingPacket) -> dict[str, Any]:
    if grounding.insufficient_evidence:
        return {"ok": False, "content": grounding.reason, "steps": []}

    steps = []
    concept = grounding.cie_concepts[0] if grounding.cie_concepts else {}
    title = concept.get("title") or ctx.topic or "Concept"
    if concept.get("definition"):
        steps.append({"step": 1, "label": "Recall verified definition", "text": concept["definition"]})
    for i, hit in enumerate(grounding.rag_hits[:2], start=2):
        steps.append({"step": i, "label": "Curriculum evidence", "text": hit.get("text") or ""})
    for a in grounding.stem_artifacts[:1]:
        payload = a.get("payload") or {}
        steps.append(
            {
                "step": len(steps) + 1,
                "label": "Verified STEM result (do not recompute here)",
                "text": str(payload.get("latex") or payload.get("result") or payload.get("equation") or payload),
            }
        )
    steps.append(
        {
            "step": len(steps) + 1,
            "label": "Check",
            "text": "Explain the last step aloud. If stuck, request Hint 2 — do not guess facts.",
        }
    )

    content = f"Worked example — **{title}** (verified sources only)\n\n"
    content += "\n".join(f"{s['step']}. **{s['label']}**: {s['text']}" for s in steps)

    return {
        "ok": True,
        "title": title,
        "steps": steps,
        "content": content,
        "citations": grounding.citations[:8],
        "policy": "stem_facts_from_engines_only",
    }
