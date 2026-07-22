"""UVIE orchestration helper — render VisualSpecs from verified lesson intelligence."""

from __future__ import annotations

from typing import Any, Mapping

from engines.universal_visual_intelligence.accessibility import apply_accessibility_variants
from engines.universal_visual_intelligence.analytics import analytics_metadata
from engines.universal_visual_intelligence.intents import resolve_visual_intents, _uli_text
from engines.universal_visual_intelligence.metadata import build_uvie_metadata
from engines.universal_visual_intelligence.priority import (
    inject_verified_visuals_into_lesson,
    merge_with_stem_preferred,
    sort_visual_specs,
)
from engines.universal_visual_intelligence.registry import run_providers
from engines.universal_visual_intelligence.schemas import VisualSpec

PACK_VERSION = "1.0.0"


def render_visual_specs(
    uli: Any = None,
    *,
    context: Mapping[str, Any] | None = None,
    max_visuals: int = 8,
) -> dict[str, Any]:
    ctx = dict(context or {})
    exam_mode = bool(ctx.get("exam_mode") or ctx.get("protected_assessment"))
    text = str(ctx.get("text") or "") or (_uli_text(uli) if uli is not None else "")
    if "sif_visuals" not in ctx and ctx.get("visuals"):
        ctx["sif_visuals"] = ctx.get("visuals")

    intents = resolve_visual_intents(uli, context=ctx, text=text)
    specs = run_providers(intents, text=text, context=ctx)
    specs = apply_accessibility_variants(specs, uli=uli)
    specs = sort_visual_specs(specs, max_visuals=max_visuals)

    preferred = merge_with_stem_preferred(
        ctx.get("preferred_visuals") or ctx.get("stem_preferred"),
        specs,
        max_visuals=max_visuals,
    )

    return {
        "ok": True,
        "version": PACK_VERSION,
        "intents": [i.to_dict() for i in intents],
        "visuals": [s.to_dict() for s in specs],
        "preferred_visuals": preferred,
        "analytics": analytics_metadata(specs),
        "lxp": {
            "important_diagrams": preferred,
            "placeholders": [s.to_dict() for s in specs if s.placeholder],
            "renderer": "lxp",
        },
        "metadata": build_uvie_metadata(
            version=PACK_VERSION,
            intent_count=len(intents),
            visual_count=len(specs),
            exam_mode=exam_mode,
            extra={
                "sources": sorted({s.source for s in specs}),
                "generative_images_enabled": False,
            },
        ),
    }


def inject_uvie_into_lesson(lesson: dict[str, Any], render_result: dict[str, Any] | None = None) -> dict[str, Any]:
    """Attach UVIE preferred visuals and clear AI diagrams when deterministic assets exist."""
    preferred = list((render_result or {}).get("preferred_visuals") or [])
    out = inject_verified_visuals_into_lesson(lesson, preferred)
    meta = dict(out.get("_meta") or {})
    meta["uvie"] = {
        "version": PACK_VERSION,
        "visual_count": len((render_result or {}).get("visuals") or []),
        "preferred_visuals": preferred,
        "lxp": (render_result or {}).get("lxp") or {},
        "mutates_curriculum": False,
    }
    out["_meta"] = meta
    out["uvie_visuals"] = (render_result or {}).get("visuals") or []
    return out


def specs_from_render(render_result: dict[str, Any]) -> list[VisualSpec]:
    out: list[VisualSpec] = []
    for item in render_result.get("visuals") or []:
        if isinstance(item, VisualSpec):
            out.append(item)
        elif isinstance(item, dict):
            out.append(
                VisualSpec(
                    visual_id=str(item.get("visual_id") or ""),
                    visual_type=str(item.get("visual_type") or ""),
                    source=str(item.get("source") or ""),
                    provenance=str(item.get("provenance") or ""),
                    caption=str(item.get("caption") or ""),
                    alt_text=str(item.get("alt_text") or ""),
                    asset_paths=list(item.get("asset_paths") or []),
                    svg=str(item.get("svg") or ""),
                    mermaid=str(item.get("mermaid") or ""),
                    invents_curriculum=bool(item.get("invents_curriculum")),
                    deterministic=bool(item.get("deterministic", True)),
                    placeholder=bool(item.get("placeholder")),
                    a11y_variants=dict(item.get("a11y_variants") or {}),
                )
            )
    return out
