"""Alerts engine — configurable thresholds, educator-facing."""

from __future__ import annotations

import uuid
from typing import Any

from engines.learning_analytics_engine.predictive_models import predictive_insights
from engines.learning_analytics_engine.schemas import AnalyticsAlert, ALERT_TYPES

DEFAULT_THRESHOLDS = {
    "risk_of_failure": 0.55,
    "risk_of_disengagement": 0.55,
    "mastery_at_risk_count": 1,
    "low_confidence": 0.4,
}


def generate_alerts(
    sources: dict[str, Any],
    *,
    thresholds: dict[str, float] | None = None,
) -> list[dict[str, Any]]:
    th = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    preds = predictive_insights(sources)
    ale = sources.get("ale") or {}
    model = ale.get("learner_model") or {}
    learner_id = (sources.get("context") or {}).get("learner_id") or ""
    alerts: list[AnalyticsAlert] = []

    risk = float(preds.get("risk_of_falling_behind") or 0)
    if risk >= th["risk_of_failure"]:
        alerts.append(
            AnalyticsAlert(
                alert_id=f"al_{uuid.uuid4().hex[:8]}",
                alert_type="learning_regression",
                severity="high" if risk >= 0.7 else "medium",
                message=f"Elevated risk of falling behind ({risk:.0%})",
                learner_id=learner_id,
                evidence=preds.get("explanatory_factors") or [],
                threshold=th["risk_of_failure"],
            )
        )
        alerts.append(
            AnalyticsAlert(
                alert_id=f"al_{uuid.uuid4().hex[:8]}",
                alert_type="teacher_attention",
                severity="high",
                message="Teacher attention recommended",
                learner_id=learner_id,
                evidence=[{"risk": risk}],
            )
        )
        alerts.append(
            AnalyticsAlert(
                alert_id=f"al_{uuid.uuid4().hex[:8]}",
                alert_type="parent_follow_up",
                severity="medium",
                message="Parent follow-up suggested for home practice",
                learner_id=learner_id,
            )
        )

    eng_risk = float(preds.get("engagement_decline_risk") or 0)
    if eng_risk >= th["risk_of_disengagement"]:
        alerts.append(
            AnalyticsAlert(
                alert_id=f"al_{uuid.uuid4().hex[:8]}",
                alert_type="low_engagement",
                severity="medium",
                message=f"Engagement decline risk ({eng_risk:.0%})",
                learner_id=learner_id,
                threshold=th["risk_of_disengagement"],
            )
        )

    at_risk = model.get("concepts_at_risk") or []
    if len(at_risk) >= th["mastery_at_risk_count"]:
        alerts.append(
            AnalyticsAlert(
                alert_id=f"al_{uuid.uuid4().hex[:8]}",
                alert_type="mastery_decline",
                severity="medium",
                message=f"{len(at_risk)} concepts at risk",
                learner_id=learner_id,
                evidence=[{"concepts": at_risk[:5]}],
            )
        )

    conf = float(model.get("confidence") or ((ale.get("confidence") or {}).get("confidence") or 0.5))
    if conf < th["low_confidence"]:
        alerts.append(
            AnalyticsAlert(
                alert_id=f"al_{uuid.uuid4().hex[:8]}",
                alert_type="accessibility_concern",
                severity="low",
                message="Low confidence — verify supports and pacing",
                learner_id=learner_id,
                evidence=[{"confidence": conf}],
                threshold=th["low_confidence"],
            )
        )

    if preds.get("assessment_readiness"):
        alerts.append(
            AnalyticsAlert(
                alert_id=f"al_{uuid.uuid4().hex[:8]}",
                alert_type="assessment_readiness",
                severity="low",
                message="Learner appears ready for assessment",
                learner_id=learner_id,
            )
        )

    mastered = model.get("concepts_mastered") or []
    if len(mastered) >= 3 and not at_risk:
        alerts.append(
            AnalyticsAlert(
                alert_id=f"al_{uuid.uuid4().hex[:8]}",
                alert_type="rapid_improvement",
                severity="low",
                message="Strong mastery band — consider enrichment",
                learner_id=learner_id,
                evidence=[{"mastered_count": len(mastered)}],
            )
        )

    # Validate alert types
    for a in alerts:
        if a.alert_type not in ALERT_TYPES:
            a.alert_type = "teacher_attention"

    return [a.to_dict() for a in alerts]
