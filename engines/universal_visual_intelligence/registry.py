"""UVIE provider registry — dispatch intents to deterministic providers."""

from __future__ import annotations

from typing import Any

from engines.universal_visual_intelligence.providers import (
    provide_computation_visuals,
    provide_geography_visuals,
    provide_knowledge_visuals,
    provide_pedagogy_visuals,
    provide_timeline_visuals,
)
from engines.universal_visual_intelligence.schemas import VisualIntent, VisualSpec, make_placeholder


def run_providers(
    intents: list[VisualIntent],
    *,
    text: str = "",
    context: dict[str, Any] | None = None,
) -> list[VisualSpec]:
    ctx = dict(context or {})
    specs: list[VisualSpec] = []
    specs.extend(
        provide_knowledge_visuals(
            intents,
            biology_figures=ctx.get("biology_figures"),
            ucf_diagrams=ctx.get("ucf_diagrams"),
        )
    )
    specs.extend(
        provide_computation_visuals(
            intents,
            stem_artifacts=ctx.get("stem_artifacts"),
        )
    )
    specs.extend(provide_pedagogy_visuals(intents, text=text, context=ctx))
    specs.extend(provide_timeline_visuals(intents, text=text, context=ctx))
    specs.extend(provide_geography_visuals(intents, text=text, context=ctx))

    covered_types = {s.visual_type for s in specs if not s.placeholder}
    covered_families = set()
    for s in specs:
        if s.placeholder:
            continue
        if s.source in {"ncert_figure"}:
            covered_families.add("knowledge")
        elif s.source in {
            "geogebra",
            "matplotlib",
            "schemdraw",
            "rdkit",
            "molecule_fallback",
            "physics_diagram",
        }:
            covered_families.add("stem")
        elif s.source == "pedagogy_organiser":
            covered_families.add("pedagogy")
        elif s.source == "timeline_scaffold":
            covered_families.add("timeline")
        elif s.source == "geography_scaffold":
            covered_families.add("geography")

    for intent in intents:
        if intent.family in covered_families:
            continue
        if intent.visual_type in covered_types:
            continue
        # Only emit placeholders for explicitly requested unresolved intents
        if intent.source_signal in {"uli", "sif", "ucf", "stem"}:
            specs.append(
                make_placeholder(
                    intent=intent,
                    reason="No deterministic provider produced an asset for this intent.",
                )
            )

    return specs
