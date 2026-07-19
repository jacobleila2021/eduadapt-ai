"""Intervention engine — wraps AME interventions with ALE explainability."""

from __future__ import annotations

from typing import Any

from engines.adaptive_learning_engine.schemas import ExplainableDecision, LearnerModel


def generate_interventions(
    model: LearnerModel,
    *,
    misconceptions: list[dict[str, Any]] | None = None,
    ame: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], ExplainableDecision]:
    ame = ame or {}
    misconceptions = misconceptions or ame.get("misconceptions") or []
    profiles = list(model.accessibility_profiles or [])

    interventions: list[dict[str, Any]] = []
    # Prefer AME package
    for row in ame.get("interventions") or []:
        interventions.append(_enrich(row, source="ame"))

    try:
        from engines.assessment_mastery_engine.interventions import (
            interventions_for_weak_concepts,
            resolve_interventions,
        )
        from engines.assessment_mastery_engine.schemas import MisconceptionHit

        if misconceptions:
            hits = []
            for m in misconceptions:
                hits.append(
                    MisconceptionHit(
                        misconception_id=m.get("misconception_id") or "misc",
                        label=m.get("label") or "",
                        concept_id=m.get("concept_id") or "",
                        confidence=float(m.get("confidence") or 0.5),
                        intervention_ids=list(m.get("intervention_ids") or []),
                    )
                )
            for rec in resolve_interventions(hits, accessibility_profiles=profiles):
                interventions.append(_enrich(rec.to_dict(), source="ame_resolve"))
        weak = model.concepts_at_risk[:6]
        for row in interventions_for_weak_concepts(weak, accessibility_profiles=profiles):
            interventions.append(_enrich(row, source="weak_concepts"))
    except Exception:  # noqa: BLE001
        pass

    # Deduplicate
    seen = set()
    unique = []
    for i in interventions:
        iid = i.get("intervention_id") or i.get("title")
        if iid in seen:
            continue
        seen.add(iid)
        unique.append(i)

    unique.sort(key=lambda r: int(r.get("priority") or 50))
    explanation = (
        f"Recommended {len(unique)} interventions because "
        f"{len(model.concepts_at_risk)} concepts are at risk and "
        f"{len(misconceptions)} misconceptions were detected; "
        f"accessibility profiles={profiles}."
    )
    decision = ExplainableDecision(
        decision_id="interv_plan",
        decision_type="intervention",
        choice=",".join(u.get("intervention_id") or "" for u in unique[:3]),
        explanation=explanation,
        evidence=[
            {"factor": "at_risk", "value": model.concepts_at_risk},
            {"factor": "misconception_count", "value": len(misconceptions)},
            {"factor": "profiles", "value": profiles},
        ],
        confidence=0.83,
    )
    return unique[:12], decision


def _enrich(row: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        **row,
        "source": source,
        "reason": row.get("reason") or row.get("description") or row.get("title"),
        "supporting_evidence": source,
        "expected_outcome": row.get("expected_outcome") or "Improve concept mastery and reduce misconception recurrence",
        "estimated_duration_min": int(row.get("estimated_duration_min") or 10),
        "success_criteria": row.get("success_criteria")
        or ["Learner explains concept correctly", "Subsequent practice score ≥ 0.75"],
        "presentation_only": True,
    }
