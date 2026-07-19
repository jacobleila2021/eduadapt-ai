"""Competency maps — CIE + AME heat/mastery/coverage (visualization only)."""

from __future__ import annotations

from typing import Any


def build_competency_map(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    outputs = context.get("engine_outputs") or {}
    cie = (outputs.get("curriculum") or {}).get("payload") or {}
    ame = (outputs.get("assessment") or {}).get("payload") or {}
    ale = (outputs.get("adaptive_learning") or {}).get("payload") or {}

    mastery = ale.get("learner_model") or ame.get("mastery") or {}
    mastered = mastery.get("concepts_mastered") or []
    at_risk = mastery.get("concepts_at_risk") or []
    if at_risk and isinstance(at_risk[0], dict):
        at_risk = [x.get("concept_id") for x in at_risk]

    heat = []
    for c in mastered[:30]:
        heat.append({"concept": c, "level": "high", "score": 0.85})
    for c in at_risk[:30]:
        heat.append({"concept": c, "level": "low", "score": 0.35})

    coverage = cie.get("coverage") or {
        "curriculum_nodes": len(mastered) + len(at_risk),
        "mastered": len(mastered),
        "gaps": len(at_risk),
    }

    return {
        "heat_map": heat,
        "mastery_map": {"mastered": mastered, "at_risk": at_risk},
        "curriculum_coverage": coverage,
        "strengths": mastered[:10],
        "gaps": at_risk[:10],
        "source": ["curriculum", "assessment"],
        "policy": "maps_visualize_verified_mastery_only",
    }
