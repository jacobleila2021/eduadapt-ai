"""Adaptation intelligence — presentation strategies only (facts locked)."""

from __future__ import annotations

from typing import Any

from engines.curriculum_intelligence_engine.ontology import get_adaptations_map
from engines.curriculum_intelligence_engine.schemas import ADAPTATION_PROFILES


def adaptations_for_concept(
    concept_id: str,
    *,
    profiles: list[str] | None = None,
    custom_map: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Recommend presentation strategies. Never alters curriculum content or STEM facts.
    """
    amap = custom_map or get_adaptations_map()
    defaults = dict(amap.get("default") or {})
    specific = dict(amap.get(concept_id) or {})
    merged = {**defaults, **specific}
    wanted = profiles or list(ADAPTATION_PROFILES)
    recommendations = {}
    for p in wanted:
        key = p.lower().replace(" ", "_")
        if key in merged:
            recommendations[key] = merged[key]
        elif p in merged:
            recommendations[key] = merged[p]
    return {
        "concept_id": concept_id,
        "policy": "presentation_only_curriculum_locked",
        "profiles": recommendations,
        "note": "CIE recommends how to present; does not change verified content.",
    }


def batch_adaptations(concept_ids: list[str]) -> dict[str, Any]:
    return {cid: adaptations_for_concept(cid) for cid in concept_ids}
