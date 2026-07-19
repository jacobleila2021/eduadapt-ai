"""Predictive analytics — wraps ALE predictions; adds LAIE confidence framing."""

from __future__ import annotations

from typing import Any


def predictive_insights(sources: dict[str, Any]) -> dict[str, Any]:
    ale = sources.get("ale") or {}
    ame = sources.get("ame") or {}
    preds = dict(ale.get("predictions") or {})
    if not preds:
        # Soft fallback from AME exam readiness
        ready = ame.get("exam_readiness") or {}
        score = float(ready.get("readiness_score") or 0)
        preds = {
            "risk_of_failure": round(max(0.0, 1.0 - score), 4),
            "probability_of_mastery": score,
            "readiness_for_assessment": ready.get("predicted_readiness") == "ready",
            "recommended_intervention_timing": "soon" if score < 0.65 else "monitor",
            "confidence": float(ready.get("confidence_level") or 0.6),
            "explanatory_factors": [
                {"factor": "exam_readiness_score", "value": score},
                {"factor": "source", "value": "ame_fallback"},
            ],
        }

    return {
        "risk_of_falling_behind": preds.get("risk_of_failure"),
        "probability_of_mastery": preds.get("probability_of_mastery"),
        "recommended_intervention_timing": preds.get("recommended_intervention_timing"),
        "revision_urgency": "high"
        if float(preds.get("risk_of_failure") or 0) >= 0.6
        else "medium"
        if float(preds.get("risk_of_failure") or 0) >= 0.4
        else "low",
        "assessment_readiness": preds.get("readiness_for_assessment"),
        "engagement_decline_risk": preds.get("risk_of_disengagement"),
        "dropout_risk_indicator": {
            "value": preds.get("risk_of_disengagement"),
            "note": "Educational engagement proxy only — not clinical",
        },
        "recommendation_confidence": preds.get("confidence") or 0.7,
        "explanatory_factors": preds.get("explanatory_factors") or [],
        "explainability": preds.get("explainability") or {},
        "educator_control": "Predictions support — never replace — educator judgment",
    }
