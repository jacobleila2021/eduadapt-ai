"""Public service API for the Universal Visual Intelligence Engine."""

from __future__ import annotations

from typing import Any, Mapping

from engines.universal_visual_intelligence.pack import (
    PACK_VERSION,
    inject_uvie_into_lesson,
    render_visual_specs,
)
from engines.universal_visual_intelligence.priority import (
    has_deterministic_visuals,
    inject_verified_visuals_into_lesson,
    select_preferred_visuals,
)

UNIVERSAL_VISUAL_INTELLIGENCE_SMOKE_OK = True


def render_visuals_for_uli(
    uli: Any = None,
    *,
    context: Mapping[str, Any] | None = None,
    max_visuals: int = 8,
) -> dict[str, Any]:
    return render_visual_specs(uli, context=context, max_visuals=max_visuals)


def inject_into_lesson(lesson: dict[str, Any], specs_or_result: Any = None) -> dict[str, Any]:
    if isinstance(specs_or_result, dict) and "preferred_visuals" in specs_or_result:
        return inject_uvie_into_lesson(lesson, specs_or_result)
    if isinstance(specs_or_result, list):
        return inject_verified_visuals_into_lesson(lesson, specs_or_result)
    return inject_uvie_into_lesson(lesson, None)


def uvie_quality_signals(uli: Any = None, *, specs: list | None = None) -> dict[str, Any]:
    from engines.universal_visual_intelligence.validation import collect_uvie_quality_signals

    return collect_uvie_quality_signals(specs, uli=uli)


def pack_health() -> dict[str, Any]:
    sample = render_visuals_for_uli(
        None,
        context={
            "text": (
                "# Water cycle process flowchart\n"
                "Students study evaporation and condensation.\n"
                "Timeline 1857 - First War of Independence.\n"
                "Geography map of India and the Ganga."
            ),
            "topic": "UVIE smoke",
            "sif_visuals": [
                {"visual_type": "flowchart", "label": "Process flowchart"},
                {"visual_type": "interactive_timeline", "label": "Timeline"},
                {"visual_type": "clickable_map", "label": "Map"},
            ],
        },
        max_visuals=8,
    )
    visuals = sample.get("visuals") or []
    preferred = sample.get("preferred_visuals") or []
    ok = (
        UNIVERSAL_VISUAL_INTELLIGENCE_SMOKE_OK
        and sample.get("ok") is True
        and sample.get("metadata", {}).get("mutates_curriculum") is False
        and sample.get("metadata", {}).get("generative_images_enabled") is False
        and len(visuals) >= 1
    )
    return {
        "ok": ok,
        "smoke": UNIVERSAL_VISUAL_INTELLIGENCE_SMOKE_OK,
        "version": PACK_VERSION,
        "visual_count": len(visuals),
        "preferred_count": len(preferred),
        "has_deterministic": has_deterministic_visuals(preferred),
        "policy": "prefer_official_then_deterministic_engines_never_ai_invent",
    }


__all__ = [
    "UNIVERSAL_VISUAL_INTELLIGENCE_SMOKE_OK",
    "PACK_VERSION",
    "render_visuals_for_uli",
    "inject_into_lesson",
    "inject_verified_visuals_into_lesson",
    "select_preferred_visuals",
    "uvie_quality_signals",
    "pack_health",
]
