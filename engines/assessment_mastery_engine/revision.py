"""Personalized revision engine — weak concepts + official practice + spacing hints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from engines.assessment_mastery_engine.exam_readiness import exam_readiness
from engines.assessment_mastery_engine.interventions import interventions_for_weak_concepts
from engines.assessment_mastery_engine.mastery import mastery_summary


def generate_revision_plan(
    learner_id: str,
    *,
    topic: str = "",
    exam_days: int | None = None,
    accessibility_profiles: list[str] | None = None,
    cie_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    summary = mastery_summary(learner_id)
    ready = exam_readiness(learner_id, topic=topic, cie_context=cie_context)
    weak_ids = [w.get("concept_id") for w in (summary.get("weak_concepts") or []) if w.get("concept_id")]
    weak_ids += [c for c in (ready.get("recommended_revision") or []) if c not in weak_ids]

    # Official practice via bank (topic keywords from weak titles/ids)
    practice_items = []
    try:
        from knowledge.question_rag import semantic_match_questions

        q = topic or " ".join(weak_ids[:3]) or "science"
        matched = semantic_match_questions(q, "", limit=6) or []
        for it in matched:
            practice_items.append(
                {
                    "item_id": it.item_id,
                    "question": it.question,
                    "official_answer": it.official_answer,
                    "bloom": it.bloom,
                    "source": it.source,
                    "topic": it.topic,
                }
            )
    except Exception:  # noqa: BLE001
        practice_items = []

    interventions = interventions_for_weak_concepts(
        weak_ids[:6],
        accessibility_profiles=accessibility_profiles,
    )

    # Spaced repetition schedule (simple)
    now = datetime.now(timezone.utc)
    intervals = [1, 3, 7, 14]
    spaced = []
    for i, cid in enumerate(weak_ids[:4]):
        spaced.append(
            {
                "concept_id": cid,
                "sessions": [
                    {"day_offset": d, "date": (now + timedelta(days=d)).date().isoformat(), "mode": "retrieval_practice"}
                    for d in intervals
                ],
            }
        )

    countdown = None
    if exam_days is not None:
        countdown = {
            "days_until_exam": exam_days,
            "priority": "high" if exam_days <= 7 else "medium" if exam_days <= 21 else "steady",
        }

    return {
        "learner_id": learner_id,
        "weak_concepts": weak_ids,
        "priority_topics": weak_ids[:5],
        "official_questions": practice_items,
        "interventions": interventions,
        "worked_examples": [i for i in interventions if i.get("kind") == "worked_example"],
        "visual_summaries": [i for i in interventions if i.get("kind") == "visual_explanation"],
        "retrieval_practice": practice_items[:4],
        "spaced_repetition": spaced,
        "exam_countdown": countdown,
        "exam_readiness": {
            "score": ready.get("readiness_score"),
            "predicted": ready.get("predicted_readiness"),
        },
        "policy": "official_bank_and_cie_only",
    }
