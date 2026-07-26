"""Learning analytics metadata — LAIE owns analytics computation."""

from __future__ import annotations

from typing import Any, Sequence


def analytics_event_template(
    *,
    interaction_events: Sequence[str] | None = None,
    engagement_signals: Sequence[str] | None = None,
    learning_objective_ids: Sequence[str] | None = None,
    competency_ids: Sequence[str] | None = None,
    misconception_ids: Sequence[str] | None = None,
    progression_markers: Sequence[str] | None = None,
    intervention_recommendations: Sequence[dict[str, Any]] | None = None,
    provenance: str = "subject_intelligence_core.analytics",
) -> dict[str, Any]:
    return {
        "interaction_events": list(interaction_events or []),
        "engagement": list(engagement_signals or []),
        "learning_objectives": list(learning_objective_ids or []),
        "competencies": list(competency_ids or []),
        "misconceptions": list(misconception_ids or []),
        "progression": list(progression_markers or []),
        "intervention_recommendations": list(intervention_recommendations or []),
        "owner": "LAIE",
        "provenance": provenance,
    }


def from_analysis(
    analysis: dict[str, Any],
    *,
    provenance: str,
) -> dict[str, Any]:
    misconceptions = list(analysis.get("misconceptions") or [])
    assess = list(analysis.get("assessment_hints") or [])
    return analytics_event_template(
        interaction_events=["lesson_open", "scaffold_step", "visual_open", "practice_attempt"],
        engagement_signals=["time_on_task", "hint_requests", "visual_interactions"],
        learning_objective_ids=[
            str(a.get("objective_ref")) for a in assess if a.get("objective_ref")
        ][:12],
        competency_ids=[
            n.get("id")
            for n in (analysis.get("concept_graph") or {}).get("nodes") or []
            if isinstance(n, dict) and n.get("type") in {"math_domain", "physics_domain", "chemistry_domain", "biology_domain", "domain"}
        ][:12],
        misconception_ids=[m.get("misconception_id") for m in misconceptions[:12]],
        progression_markers=["introduced", "practised", "reviewed"],
        intervention_recommendations=[
            {
                "misconception_id": m.get("misconception_id"),
                "strategy": m.get("correction_strategy"),
            }
            for m in misconceptions[:6]
        ],
        provenance=provenance,
    )
