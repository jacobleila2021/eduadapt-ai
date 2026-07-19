"""Multimodal references — prefer deterministic assets from existing engines."""

from __future__ import annotations

from typing import Any

from engines.ai_tutor_intelligence_engine.schemas import GroundingPacket, TutorContext


def multimodal_bundle(
    ctx: TutorContext,
    grounding: GroundingPacket,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    outputs = context.get("engine_outputs") or {}
    sa = (outputs.get("scientific_accuracy") or {}).get("payload") or {}
    aie = (outputs.get("accessibility") or {}).get("payload") or {}

    assets = []
    for a in grounding.stem_artifacts or sa.get("artifacts") or []:
        if not isinstance(a, dict):
            continue
        payload = a.get("payload") or {}
        kind = a.get("kind") or a.get("engine_id") or "stem"
        assets.append(
            {
                "kind": kind,
                "prefer": "deterministic",
                "latex": payload.get("latex"),
                "svg_or_path": payload.get("svg") or payload.get("path") or payload.get("image"),
                "note": "Use engine asset — do not AI-invent diagrams",
            }
        )

    return {
        "verified_diagrams": [a for a in assets if a.get("svg_or_path")],
        "expressions": [a for a in assets if a.get("latex")],
        "audio_narration": {
            "available": True,
            "integrates": "audio_learning.py",
            "preferred": "auditory" in ctx.accessibility_profiles
            or ((aie.get("presentation") or {}).get("primary_mode") == "auditory"),
        },
        "captions": True,
        "highlighted_text": aie.get("interface_css_hints") or {},
        "policy": "deterministic_assets_over_ai_illustrations",
    }
