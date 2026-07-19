"""Spaced repetition scheduler — evidence-based intervals."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from engines.adaptive_learning_engine.schemas import REVIEW_INTERVALS_DAYS, ExplainableDecision, LearnerModel


def schedule_reviews(
    model: LearnerModel,
    concept_ids: list[str] | None = None,
    *,
    forgetting_risk: float | None = None,
) -> tuple[list[dict[str, Any]], ExplainableDecision]:
    now = datetime.now(timezone.utc)
    concepts = concept_ids or list(dict.fromkeys((model.concepts_at_risk or []) + (model.concepts_developing or [])))
    confidence = float(model.confidence or 0.5)
    risk = forgetting_risk
    if risk is None:
        risk = 0.7 if model.concepts_at_risk else (0.4 if model.concepts_developing else 0.25)
        risk = max(0.1, min(0.95, risk + (0.5 - confidence) * 0.3))

    # Higher risk → denser early reviews
    if risk >= 0.65:
        intervals = [0, 1, 3, 7, 14]
    elif risk >= 0.4:
        intervals = [1, 3, 7, 14, 30]
    else:
        intervals = [3, 7, 14, 30, 60]

    schedule = []
    for cid in concepts[:8]:
        sessions = []
        for d in intervals:
            if d not in REVIEW_INTERVALS_DAYS and d != 0:
                continue
            sessions.append(
                {
                    "day_offset": d,
                    "date": (now + timedelta(days=d)).date().isoformat(),
                    "mode": "immediate_review" if d == 0 else "spaced_retrieval",
                }
            )
        schedule.append({"concept_id": cid, "sessions": sessions, "forgetting_risk": round(risk, 3)})

    explanation = (
        f"Spaced reviews for {len(schedule)} concepts using intervals {intervals} days "
        f"because forgetting_risk={risk:.2f} and confidence={confidence:.0%}."
    )
    decision = ExplainableDecision(
        decision_id="sr_schedule",
        decision_type="spaced_repetition",
        choice=str(intervals),
        explanation=explanation,
        evidence=[
            {"factor": "forgetting_risk", "value": risk},
            {"factor": "confidence", "value": confidence},
            {"factor": "concept_count", "value": len(schedule)},
        ],
        confidence=0.84,
    )
    return schedule, decision
