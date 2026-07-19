"""Skill trees from CIE concepts — prerequisites & next skills (presentation)."""

from __future__ import annotations

from typing import Any


def build_skill_tree(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    outputs = context.get("engine_outputs") or {}
    cie = (outputs.get("curriculum") or {}).get("payload") or {}
    ame = (outputs.get("assessment") or {}).get("payload") or {}
    ale = (outputs.get("adaptive_learning") or {}).get("payload") or {}
    ucf = (outputs.get("universal_curriculum") or {}).get("payload") or {}

    # Prefer UCF competencies/topics when available
    ucf_concepts = ((ucf.get("adapters") or {}).get("lmas") or {}).get("concepts") or []
    concepts = (
        [c.get("id") for c in ucf_concepts if isinstance(c, dict)]
        or cie.get("concepts")
        or cie.get("learning_objectives")
        or context.get("concepts")
        or ["foundations", "core_idea", "application", "enrichment"]
    )
    if concepts and isinstance(concepts[0], dict):
        concepts = [c.get("id") or c.get("name") or c.get("concept_id") or str(c) for c in concepts]

    mastery = ale.get("learner_model") or ame.get("mastery") or {}
    mastered = set(mastery.get("concepts_mastered") or [])
    at_risk = mastery.get("concepts_at_risk") or []
    if at_risk and isinstance(at_risk[0], dict):
        at_risk = [x.get("concept_id") for x in at_risk]
    at_risk_set = set(at_risk or [])

    # UCF prerequisite map when present
    prereq_map = {c.get("id"): list(c.get("prerequisites") or []) for c in ucf_concepts if isinstance(c, dict)}

    nodes = []
    for i, cid in enumerate(concepts[:24]):
        status = "mastered" if cid in mastered else ("current" if cid in at_risk_set or i == 0 else "locked")
        if status == "locked" and i > 0 and concepts[i - 1] in mastered:
            status = "recommended"
        nodes.append(
            {
                "concept_id": cid,
                "prerequisites": prereq_map.get(cid) or ([concepts[i - 1]] if i else []),
                "status": status,
            }
        )

    recommended = [n["concept_id"] for n in nodes if n["status"] in ("recommended", "current")][:5]
    enrichment = [n["concept_id"] for n in nodes if n["status"] == "mastered"][-3:]

    return {
        "nodes": nodes,
        "mastered": list(mastered)[:20],
        "current": [n["concept_id"] for n in nodes if n["status"] == "current"],
        "recommended_next": recommended,
        "enrichment_paths": enrichment,
        "source": ["universal_curriculum", "curriculum", "assessment", "adaptive_learning"]
        if ucf_concepts
        else ["curriculum", "assessment", "adaptive_learning"],
        "interactive": True,
    }
