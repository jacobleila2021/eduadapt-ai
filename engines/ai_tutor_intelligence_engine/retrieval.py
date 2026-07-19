"""Verified retrieval — KIE/CIE/AME/STEM/RAG before any tutoring text."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import GroundingPacket, TutorContext


def retrieve_grounding(ctx: TutorContext, context: dict[str, Any] | None = None) -> GroundingPacket:
    """
    Retrieve verified evidence. Never invent STEM facts or official answers.
    """
    context = context or {}
    outputs = context.get("engine_outputs") or {}
    citations: list[str] = []
    rag_hits: list[dict[str, Any]] = []
    stem: list[dict[str, Any]] = []
    official: list[dict[str, Any]] = []
    concepts: list[dict[str, Any]] = []

    # STEM artifacts from Scientific Accuracy Engine
    sa = (outputs.get("scientific_accuracy") or {}).get("payload") or {}
    for a in sa.get("artifacts") or []:
        if isinstance(a, dict):
            stem.append(a)
            cite = (a.get("payload") or {}).get("citation") or a.get("engine_id")
            if cite:
                citations.append(str(cite))

    # Curriculum knowledge / RAG from curriculum stage
    curr = (outputs.get("curriculum") or {}).get("payload") or {}
    knowledge = curr.get("knowledge") or {}
    for hit in knowledge.get("rag_hits") or knowledge.get("hits") or []:
        if isinstance(hit, dict):
            rag_hits.append(
                {
                    "text": (hit.get("text") or "")[:500],
                    "citation": hit.get("citation") or hit.get("chunk_id"),
                    "score": hit.get("score"),
                }
            )
            if hit.get("citation"):
                citations.append(str(hit["citation"]))
    for c in knowledge.get("citations") or []:
        citations.append(str(c))

    cie = curr.get("curriculum_intelligence") or {}
    for m in cie.get("matched_concepts") or []:
        if isinstance(m, dict):
            concepts.append(m)
            if m.get("definition"):
                rag_hits.append(
                    {
                        "text": f"{m.get('title')}: {m.get('definition')}",
                        "citation": f"CIE:{m.get('concept_id')}",
                        "score": 1.0,
                    }
                )
                citations.append(f"CIE:{m.get('concept_id')}")

    # Official items (for practice guidance — do not reveal keys unless allowed)
    ame = (outputs.get("assessment") or {}).get("payload") or {}
    for it in ame.get("official_mcqs") or []:
        if isinstance(it, dict):
            official.append(
                {
                    "item_id": it.get("item_id"),
                    "question": it.get("question"),
                    "source": it.get("source"),
                    "bloom": it.get("bloom"),
                    # official_answer omitted from tutor-facing packet by default
                }
            )

    # Live RAG fallback if empty
    if not rag_hits and (ctx.topic or ctx.lesson_excerpt):
        try:
            from knowledge.service import prepare_knowledge_for_lesson

            kn = prepare_knowledge_for_lesson(
                ctx.lesson_excerpt or ctx.topic,
                {"topic": ctx.topic, "grade_level": ctx.grade},
            )
            for hit in kn.get("rag_hits") or kn.get("hits") or []:
                if isinstance(hit, dict):
                    rag_hits.append(
                        {
                            "text": (hit.get("text") or "")[:500],
                            "citation": hit.get("citation"),
                            "score": hit.get("score"),
                        }
                    )
                    if hit.get("citation"):
                        citations.append(str(hit["citation"]))
            for c in kn.get("citations") or []:
                citations.append(str(c))
            for it in kn.get("official_mcqs") or []:
                if isinstance(it, dict):
                    official.append(
                        {
                            "item_id": it.get("item_id") or it.get("id"),
                            "question": it.get("question"),
                            "source": it.get("source"),
                        }
                    )
        except Exception:  # noqa: BLE001
            pass

    # CIE ontology definitions if still thin
    if not concepts and ctx.concept_ids:
        try:
            from engines.curriculum_intelligence_engine.intelligence import get_runtime

            g = get_runtime()["graph"]
            for cid in ctx.concept_ids[:5]:
                n = g.get_concept(cid)
                if n:
                    concepts.append(n.to_dict())
                    rag_hits.append(
                        {
                            "text": f"{n.title}: {n.definition}",
                            "citation": f"CIE:{n.concept_id}",
                            "score": 1.0,
                        }
                    )
                    citations.append(f"CIE:{n.concept_id}")
        except Exception:  # noqa: BLE001
            pass

    evidence_score = len(rag_hits) + len(stem) + len(concepts) + (1 if ctx.lesson_excerpt else 0)
    insufficient = evidence_score < 1
    reason = ""
    if insufficient:
        reason = (
            "Insufficient verified evidence from KIE/CIE/STEM/RAG. "
            "I cannot answer confidently — please review the lesson or ask your teacher."
        )

    return GroundingPacket(
        ok=not insufficient,
        citations=list(dict.fromkeys(citations))[:20],
        rag_hits=rag_hits[:8],
        stem_artifacts=stem[:8],
        official_items=official[:6],
        cie_concepts=concepts[:8],
        insufficient_evidence=insufficient,
        reason=reason,
    )
