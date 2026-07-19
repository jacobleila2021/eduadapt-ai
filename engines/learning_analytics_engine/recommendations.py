"""Prescriptive recommendations — explainable, auditable."""

from __future__ import annotations

import uuid
from typing import Any

from engines.learning_analytics_engine.schemas import InsightRecommendation
from engines.learning_analytics_engine.predictive_models import predictive_insights


def build_insight_recommendations(sources: dict[str, Any]) -> list[dict[str, Any]]:
    ale = sources.get("ale") or {}
    ame = sources.get("ame") or {}
    aie = sources.get("aie") or {}
    preds = predictive_insights(sources)
    out: list[InsightRecommendation] = []

    # Prefer ALE/AME verified recs
    for row in (ale.get("interventions") or [])[:5]:
        out.append(
            InsightRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                audience="teacher",
                title=row.get("title") or "Intervention",
                reason=row.get("reason") or row.get("description") or "At-risk mastery / misconception",
                evidence=[{"source": "ame_ale_intervention", "id": row.get("intervention_id")}],
                confidence=0.82,
                priority=int(row.get("priority") or 30),
                expected_outcome=row.get("expected_outcome") or "Improve mastery and reduce misconception",
                kind="intervention",
            )
        )

    if float(preds.get("risk_of_falling_behind") or 0) >= 0.5:
        out.append(
            InsightRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                audience="teacher",
                title="Teacher conference / small-group reteach",
                reason="Elevated risk of falling behind",
                evidence=preds.get("explanatory_factors") or [],
                confidence=float(preds.get("recommendation_confidence") or 0.7),
                priority=10,
                expected_outcome="Stabilize mastery trajectory",
                kind="intervention",
            )
        )
        out.append(
            InsightRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                audience="parent",
                title="Parent follow-up: short official practice",
                reason="Home support recommended due to risk indicators",
                evidence=[{"factor": "revision_urgency", "value": preds.get("revision_urgency")}],
                confidence=0.75,
                priority=20,
                expected_outcome="Increase retrieval practice consistency",
                kind="practice",
            )
        )

    if (aie.get("learner_profile") or {}).get("active_profiles"):
        out.append(
            InsightRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                audience="special_educator",
                title="Verify accessibility accommodations are applied",
                reason="Active accessibility profiles present",
                evidence=[{"profiles": (aie.get("learner_profile") or {}).get("active_profiles")}],
                confidence=0.9,
                priority=15,
                expected_outcome="Supports match learner needs without changing curriculum",
                kind="accessibility",
            )
        )

    for row in ale.get("enrichment") or []:
        out.append(
            InsightRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                audience="teacher",
                title=row.get("title") or "Enrichment",
                reason=row.get("rationale") or "Ready for extension",
                evidence=[{"source": "ale_enrichment"}],
                confidence=0.78,
                priority=40,
                expected_outcome="Maintain challenge without removing scaffolds",
                kind="enrichment",
            )
        )

    if (ame.get("exam_readiness") or {}).get("predicted_readiness") == "needs_revision":
        out.append(
            InsightRecommendation(
                recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
                audience="student",
                title="Revision session",
                reason="Exam readiness indicates needs_revision",
                evidence=[{"exam_readiness": ame.get("exam_readiness")}],
                confidence=0.8,
                priority=12,
                expected_outcome="Improve readiness score via spaced retrieval",
                kind="revision",
            )
        )

    out.append(
        InsightRecommendation(
            recommendation_id=f"rec_{uuid.uuid4().hex[:8]}",
            audience="student",
            title="AI Tutor session on next activity",
            reason="Targeted tutoring from ALE next activity",
            evidence=[{"next_activity": ale.get("next_activity")}],
            confidence=0.77,
            priority=25,
            expected_outcome="Clarify misconceptions with verified grounding",
            kind="intervention",
        )
    )

    out.sort(key=lambda r: r.priority)
    return [r.to_dict() for r in out]
