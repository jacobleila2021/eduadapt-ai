"""Enrichment engine — extension for ready learners."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.schemas import ExplainableDecision, LearnerModel


def generate_enrichment(
    model: LearnerModel,
    *,
    cie: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], ExplainableDecision]:
    cie = cie or {}
    ready = bool(model.concepts_mastered) and not model.concepts_at_risk
    gifted = bool(set(model.accessibility_profiles or []).intersection({"gifted", "twice_exceptional"}))
    high_conf = float(model.confidence or 0) >= 0.75

    plans: list[dict[str, Any]] = []
    if ready or gifted or high_conf:
        cross = []
        for m in cie.get("matched_concepts") or []:
            cross.extend(m.get("related_concepts") or [])
        # CIE cross-curriculum advanced links
        for link in cie.get("cross_curriculum") or []:
            if link.get("link_type") == "advanced":
                plans.append(
                    {
                        "kind": "cross_disciplinary",
                        "title": f"Explore {link.get('label')} ({link.get('board')})",
                        "concept_id": link.get("concept_id"),
                        "rationale": "Advanced cross-curriculum link",
                    }
                )
        plans.extend(
            [
                {
                    "kind": "challenge_problems",
                    "title": "Challenge set from official HOTS/competency bank",
                    "source": "official_question_bank",
                    "rationale": "Mastery band supports extension",
                },
                {
                    "kind": "inquiry",
                    "title": "Inquiry / research mini-task",
                    "rationale": "Higher-order thinking extension",
                },
                {
                    "kind": "real_world",
                    "title": "Real-world application prompt",
                    "rationale": "Transfer of learning",
                },
            ]
        )
        if gifted:
            plans.append(
                {
                    "kind": "olympiad_style",
                    "title": "Olympiad-style stretch item (presentation challenge)",
                    "rationale": "Gifted enrichment pathway",
                    "note": "Facts still from verified engines/bank",
                }
            )

    explanation = (
        f"Enrichment {'recommended' if plans else 'not recommended'}: "
        f"mastered={len(model.concepts_mastered)}, at_risk={len(model.concepts_at_risk)}, "
        f"gifted={gifted}, confidence={model.confidence:.0%}."
    )
    decision = ExplainableDecision(
        decision_id="enrich_plan",
        decision_type="enrichment",
        choice="enrich" if plans else "defer",
        explanation=explanation,
        evidence=[
            {"factor": "ready", "value": ready},
            {"factor": "gifted", "value": gifted},
            {"factor": "confidence", "value": model.confidence},
        ],
        confidence=0.8,
    )
    return plans[:8], decision
