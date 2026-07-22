"""UVIE priority — extends engines.visualization.priority without conflicting order."""

from __future__ import annotations

from typing import Any

from engines.universal_visual_intelligence.schemas import VisualSpec
from engines.visualization.priority import (
    PRIORITY_ORDER as _BASE_PRIORITY_ORDER,
    has_deterministic_visuals,
    inject_verified_visuals_into_lesson,
    select_preferred_visuals,
    visualization_prompt_rules,
)

# Insert organisers before ai_illustration; placeholders last.
_EXTENDED: list[str] = []
for name in _BASE_PRIORITY_ORDER:
    if name == "ai_illustration":
        _EXTENDED.extend(
            [
                "pedagogy_organiser",
                "timeline_scaffold",
                "geography_scaffold",
            ]
        )
    _EXTENDED.append(name)
if "pedagogy_organiser" not in _EXTENDED:
    _EXTENDED.extend(["pedagogy_organiser", "timeline_scaffold", "geography_scaffold"])
if "placeholder" not in _EXTENDED:
    _EXTENDED.append("placeholder")

PRIORITY_ORDER: tuple[str, ...] = tuple(_EXTENDED)


def rank_source(source: str) -> int:
    rank = {name: i for i, name in enumerate(PRIORITY_ORDER)}
    return rank.get(source or "placeholder", 98)


def sort_visual_specs(specs: list[VisualSpec], *, max_visuals: int = 8) -> list[VisualSpec]:
    ordered = sorted(specs, key=lambda s: (rank_source(s.source), s.visual_id))
    seen: set[str] = set()
    unique: list[VisualSpec] = []
    for spec in ordered:
        key = f"{spec.source}:{spec.caption}:{','.join(spec.asset_paths)}:{spec.visual_type}"
        if key in seen:
            continue
        seen.add(key)
        unique.append(spec)
        if len(unique) >= max_visuals:
            break
    return unique


def specs_to_preferred(specs: list[VisualSpec]) -> list[dict[str, Any]]:
    return [s.to_preferred_visual() for s in specs]


def merge_with_stem_preferred(
    stem_preferred: list[dict[str, Any]] | None,
    uvie_specs: list[VisualSpec],
    *,
    max_visuals: int = 8,
) -> list[dict[str, Any]]:
    """Merge SAE/STEM preferred visuals with UVIE specs; STEM/knowledge win on ties."""
    converted: list[VisualSpec] = []
    for i, v in enumerate(stem_preferred or []):
        if not isinstance(v, dict):
            continue
        converted.append(
            VisualSpec(
                visual_id=str(v.get("visual_id") or f"stem:{i}"),
                visual_type=str(v.get("visual_type") or v.get("task_kind") or "stem_visual"),
                source=str(v.get("source") or "matplotlib"),
                provenance="lesson_pipeline.preferred_visuals",
                caption=str(v.get("caption") or ""),
                alt_text=str(v.get("alt_text") or v.get("caption") or "Verified STEM visual"),
                asset_paths=list(v.get("asset_paths") or []),
                iframe_url=v.get("iframe_url"),
                latex=v.get("latex"),
                svg=str(v.get("svg") or ""),
                mermaid=str(v.get("mermaid") or ""),
                invents_curriculum=False,
                deterministic=str(v.get("source") or "") != "ai_illustration",
                engine_id=str(v.get("engine_id") or ""),
                task_kind=str(v.get("task_kind") or ""),
            )
        )
    merged = sort_visual_specs(converted + list(uvie_specs), max_visuals=max_visuals)
    return specs_to_preferred(merged)


__all__ = [
    "PRIORITY_ORDER",
    "rank_source",
    "sort_visual_specs",
    "specs_to_preferred",
    "merge_with_stem_preferred",
    "select_preferred_visuals",
    "has_deterministic_visuals",
    "visualization_prompt_rules",
    "inject_verified_visuals_into_lesson",
]
