"""Visualization metadata helpers (animations, simulations, concept maps)."""

from __future__ import annotations

from typing import Any, Sequence


def visualization_hooks(
    *,
    animations: Sequence[str] | None = None,
    interactive_diagrams: Sequence[str] | None = None,
    simulations: Sequence[str] | None = None,
    timelines: Sequence[str] | None = None,
    process_diagrams: Sequence[str] | None = None,
    concept_maps: Sequence[str] | None = None,
    visual_summaries: Sequence[str] | None = None,
    provenance: str = "subject_intelligence_core.visualization",
) -> dict[str, Any]:
    return {
        "animations": list(animations or []),
        "interactive_diagrams": list(interactive_diagrams or []),
        "simulations": list(simulations or []),
        "timelines": list(timelines or []),
        "process_diagrams": list(process_diagrams or []),
        "concept_maps": list(concept_maps or []),
        "visual_summaries": list(visual_summaries or []),
        "renderer": "lxp_or_vmle",
        "provenance": provenance,
    }


def hooks_from_visual_types(visuals: list[dict[str, Any]], *, provenance: str) -> dict[str, Any]:
    types = [str(v.get("visual_type") or "") for v in visuals]
    return visualization_hooks(
        interactive_diagrams=[t for t in types if "interactive" in t or "viewer" in t],
        simulations=[t for t in types if "simulation" in t],
        animations=[t for t in types if "animation" in t],
        process_diagrams=[t for t in types if "process" in t or "flow" in t],
        concept_maps=[t for t in types if "concept_map" in t],
        visual_summaries=[t for t in types if "summary" in t],
        provenance=provenance,
    )
