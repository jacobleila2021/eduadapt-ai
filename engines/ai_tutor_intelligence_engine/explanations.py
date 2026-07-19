"""Grounded explanation templates — facts from retrieval only."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import GroundingPacket, TutorContext


def generate_explanation(
    ctx: TutorContext,
    grounding: GroundingPacket,
    *,
    depth: str = "developing",
    personalization: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if grounding.insufficient_evidence or not grounding.ok:
        return {
            "ok": False,
            "depth": depth,
            "content": grounding.reason
            or "I do not have enough verified curriculum evidence to explain this confidently. "
            "Please review the lesson or ask your teacher.",
            "citations": [],
            "policy": "refuse_without_grounding",
        }

    personalization = personalization or {}
    concept = (grounding.cie_concepts[0] if grounding.cie_concepts else {}) or {}
    title = concept.get("title") or ctx.topic or "this concept"
    definition = concept.get("definition") or ""
    evidence_bits = []
    for hit in grounding.rag_hits[:3]:
        t = (hit.get("text") or "").strip()
        if t:
            evidence_bits.append(t)
    if definition and definition not in evidence_bits:
        evidence_bits.insert(0, f"{title}: {definition}")

    # STEM formula snippets if present (do not recompute — display payload only)
    stem_notes = []
    for a in grounding.stem_artifacts[:2]:
        payload = a.get("payload") or {}
        if payload.get("latex") or payload.get("result") or payload.get("equation"):
            stem_notes.append(
                str(payload.get("latex") or payload.get("equation") or payload.get("result"))
            )

    simplify = personalization.get("simplify_vocabulary")
    chunk = personalization.get("chunk_steps")

    if depth == "beginner":
        body = (
            f"Let's learn about **{title}**.\n\n"
            f"{evidence_bits[0] if evidence_bits else 'See your lesson for the verified definition.'}\n\n"
            "Remember: we only use facts from your curriculum materials."
        )
    elif depth == "developing":
        body = (
            f"**{title}**\n\n"
            + "\n\n".join(f"- {b}" for b in evidence_bits[:2])
            + ("\n\nVerified relation: " + "; ".join(stem_notes) if stem_notes else "")
        )
    elif depth in ("advanced", "expert"):
        body = (
            f"**{title}** ({depth} depth)\n\n"
            + "\n\n".join(evidence_bits[:4])
            + ("\n\nSTEM (verified): " + "; ".join(stem_notes) if stem_notes else "")
            + "\n\nTry connecting this to a related prerequisite or application from your pathway."
        )
    else:  # proficient
        body = (
            f"**{title}**\n\n"
            + "\n\n".join(evidence_bits[:3])
            + ("\n\n" + "; ".join(stem_notes) if stem_notes else "")
        )

    if simplify:
        body = body.replace("consequently", "so").replace("therefore", "so")
    if chunk:
        body = body.replace("\n\n", "\n\n→ ")

    if personalization.get("use_visuals_first"):
        body = "First, look at any verified diagram for this topic, then read:\n\n" + body

    return {
        "ok": True,
        "depth": depth,
        "content": body,
        "citations": grounding.citations[:10],
        "concept_id": concept.get("concept_id"),
        "objectives": ctx.learning_objectives[:3],
        "policy": "presentation_only_facts_from_grounding",
    }
