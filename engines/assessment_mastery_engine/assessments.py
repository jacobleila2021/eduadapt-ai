"""Assessment builders — diagnostic / formative / summative / competency from official bank."""

from __future__ import annotations

import uuid
from typing import Any

from engines.assessment_mastery_engine.schemas import AssessmentItemRef


def _items_from_official(matched: list[Any], *, concept_id: str = "") -> list[AssessmentItemRef]:
    out: list[AssessmentItemRef] = []
    for it in matched:
        # OfficialMcq dataclass or dict
        if hasattr(it, "item_id"):
            out.append(
                AssessmentItemRef(
                    item_id=it.item_id,
                    question_type=getattr(it, "question_type", "mcq") or "mcq",
                    concept_id=concept_id,
                    bloom=getattr(it, "bloom", "remember") or "remember",
                    difficulty=getattr(it, "difficulty", "medium") or "medium",
                    marks=int(getattr(it, "marks", 1) or 1),
                    source=getattr(it, "source", "") or "",
                    board=getattr(it, "board", "") or "",
                    chapter=int(getattr(it, "chapter", 0) or 0),
                    topic=getattr(it, "topic", "") or "",
                    official_answer=getattr(it, "official_answer", "") or "",
                    question=getattr(it, "question", "") or "",
                    learning_outcome_id=getattr(it, "learning_objective", "") or "",
                )
            )
        elif isinstance(it, dict):
            out.append(
                AssessmentItemRef(
                    item_id=str(it.get("item_id") or it.get("id") or ""),
                    question_type=str(it.get("question_type") or "mcq"),
                    concept_id=concept_id,
                    bloom=str(it.get("bloom") or "remember"),
                    difficulty=str(it.get("difficulty") or "medium"),
                    marks=int(it.get("marks") or 1),
                    source=str(it.get("source") or ""),
                    board=str(it.get("board") or ""),
                    chapter=int(it.get("chapter") or 0),
                    topic=str(it.get("topic") or ""),
                    official_answer=str(it.get("official_answer") or ""),
                    question=str(it.get("question") or ""),
                    learning_outcome_id=str(it.get("learning_objective") or ""),
                )
            )
    return out


def _fetch_bank(topic: str, lesson: str, limit: int) -> list[Any]:
    from knowledge.question_rag import semantic_match_questions

    return list(semantic_match_questions(topic, lesson, limit=limit) or [])


def _fetch_bundle(topic: str) -> dict[str, list[Any]]:
    from knowledge.question_bank import match_exam_bundle

    return match_exam_bundle(topic, limit_per_type=3) or {}


def generate_assessment(
    *,
    assessment_type: str = "formative",
    topic: str = "",
    lesson_text: str = "",
    concept_ids: list[str] | None = None,
    limit: int = 6,
    learner_id: str = "",
    cie_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Build an assessment package from official bank only.
    Does not invent questions or answers.
    """
    aid = f"as_{assessment_type}_{uuid.uuid4().hex[:8]}"
    concept_id = (concept_ids or [""])[0] if concept_ids else ""
    if cie_context and not concept_id:
        concept_id = cie_context.get("primary_concept_id") or ""

    matched = _fetch_bank(topic, lesson_text, limit=limit)
    items = _items_from_official(matched, concept_id=concept_id)
    bundle = {}
    if assessment_type in ("summative", "diagnostic", "competency"):
        raw = _fetch_bundle(topic or (items[0].topic if items else ""))
        bundle = {
            k: [x.to_dict() for x in _items_from_official(v, concept_id=concept_id)]
            for k, v in raw.items()
        }

    meta: dict[str, Any] = {
        "assessment_id": aid,
        "assessment_type": assessment_type,
        "topic": topic,
        "learner_id": learner_id,
        "concept_ids": concept_ids or ([concept_id] if concept_id else []),
        "item_count": len(items),
        "items": [i.to_dict() for i in items],
        "exam_bundle": bundle,
        "policy": {
            "official_answers_only": True,
            "no_llm_answer_keys": True,
            "presentation_adaptable": True,
        },
    }

    if assessment_type == "diagnostic":
        # Prefer prerequisite concepts from CIE when available
        gaps = (cie_context or {}).get("learning_gaps") or {}
        meta["diagnostic"] = {
            "missing_prerequisites": gaps.get("missing_prerequisites") or [],
            "recommend_starting_point": (gaps.get("remediation") or [{}])[0].get("concept_id")
            or concept_id,
            "purpose": "prior_knowledge_and_gaps",
        }
    elif assessment_type == "formative":
        meta["formative"] = {
            "modes": ["exit_ticket", "quick_check", "confidence_rating"],
            "suggested_mode": "quick_check" if len(items) <= 3 else "exit_ticket",
        }
    elif assessment_type == "summative":
        meta["summative"] = {
            "formats": ["chapter_test", "unit_test"],
            "includes_exam_bundle": bool(bundle),
        }
    elif assessment_type == "competency":
        comps = (cie_context or {}).get("competencies") or []
        meta["competency"] = {
            "competencies": comps,
            "independent_of_chapter_order": True,
        }

    return meta
