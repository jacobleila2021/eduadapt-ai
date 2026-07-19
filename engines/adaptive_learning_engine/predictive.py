"""Predictive learning — risk scores with confidence + explanatory factors."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.schemas import ExplainableDecision, LearnerModel


def predict_outcomes(model: LearnerModel, *, ame: dict[str, Any] | None = None) -> dict[str, Any]:
    ame = ame or {}
    at_risk_n = len(model.concepts_at_risk or [])
    mastered_n = len(model.concepts_mastered or [])
    conf = float(model.confidence or 0.5)
    completion = float(model.completion_rate or 0.5)
    motivation = float(model.motivation_level or 0.5)

    failure_risk = min(0.95, 0.15 + 0.12 * at_risk_n + (0.5 - conf) * 0.4 + (0.5 - completion) * 0.2)
    disengagement_risk = min(0.95, 0.1 + (0.5 - motivation) * 0.5 + (0.5 - completion) * 0.3)
    if "adhd" in (model.accessibility_profiles or []) and model.time_on_task_min and model.time_on_task_min < 5:
        disengagement_risk = min(0.95, disengagement_risk + 0.1)

    mastery_prob = max(0.05, min(0.95, 0.2 + 0.08 * mastered_n + conf * 0.4 - 0.05 * at_risk_n))
    est_minutes = 15 * max(1, at_risk_n + len(model.concepts_developing or []))
    intervention_timing = "immediate" if failure_risk >= 0.6 else "soon" if failure_risk >= 0.4 else "monitor"
    assessment_ready = mastery_prob >= 0.7 and at_risk_n == 0

    factors = [
        {"factor": "at_risk_concepts", "value": at_risk_n},
        {"factor": "mastered_concepts", "value": mastered_n},
        {"factor": "confidence", "value": conf},
        {"factor": "completion_rate", "value": completion},
        {"factor": "motivation", "value": motivation},
    ]
    explanation = (
        f"Predicted failure_risk={failure_risk:.0%}, disengagement={disengagement_risk:.0%}, "
        f"mastery_probability={mastery_prob:.0%}, assessment_ready={assessment_ready} "
        f"from mastery evidence and engagement signals."
    )
    decision = ExplainableDecision(
        decision_id="predict",
        decision_type="prediction",
        choice=intervention_timing,
        explanation=explanation,
        evidence=factors,
        confidence=0.72,
    )
    return {
        "risk_of_failure": round(failure_risk, 4),
        "risk_of_disengagement": round(disengagement_risk, 4),
        "probability_of_mastery": round(mastery_prob, 4),
        "estimated_completion_time_min": est_minutes,
        "recommended_intervention_timing": intervention_timing,
        "readiness_for_assessment": assessment_ready,
        "confidence": decision.confidence,
        "explanatory_factors": factors,
        "explainability": decision.to_dict(),
        "exam_readiness_ref": ame.get("exam_readiness") or {},
    }
