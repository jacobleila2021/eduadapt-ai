"""Diagram / figure metadata standardization — LXP/VMLE render."""

from __future__ import annotations

from typing import Any, Mapping, Sequence


def recommend_visuals_from_catalogue(
    domains: list[dict[str, Any]],
    catalogue: Mapping[str, Sequence[Mapping[str, str]]],
    *,
    provenance: str,
    limit: int = 10,
    default_visual: Mapping[str, str] | None = None,
    renderer: str = "lxp_or_vmle",
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for d in domains:
        for vis in catalogue.get(d["domain"], []):
            key = vis["visual_type"]
            if key in seen:
                continue
            seen.add(key)
            out.append(
                {
                    **dict(vis),
                    "domain": d["domain"],
                    "renderer": renderer,
                    "provenance": provenance,
                }
            )
            if len(out) >= limit:
                return out
    if not out:
        fallback = dict(
            default_visual
            or {
                "visual_type": "concept_map",
                "label": "Concept map",
            }
        )
        out.append(
            {
                **fallback,
                "domain": "general",
                "renderer": renderer,
                "provenance": provenance,
            }
        )
    return out


def diagram_bundle(
    domains: list[dict[str, Any]],
    visuals: list[dict[str, Any]],
    *,
    frameworks: Sequence[str],
    suggested_sequence: Sequence[str],
    provenance: str,
) -> dict[str, Any]:
    return {
        "frameworks": list(frameworks),
        "suggested_sequence": list(suggested_sequence),
        "active_domains": [d["domain"] for d in domains],
        "recommended_diagrams": visuals,
        "provenance": provenance,
    }
