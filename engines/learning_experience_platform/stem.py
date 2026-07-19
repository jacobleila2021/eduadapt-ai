"""Interactive STEM panel descriptors — verified engines only."""

from __future__ import annotations

from typing import Any


def stem_interactives(context: dict[str, Any] | None = None) -> dict[str, Any]:
    context = context or {}
    outputs = context.get("engine_outputs") or {}
    sa = (outputs.get("scientific_accuracy") or {}).get("payload") or {}
    artifacts = list(sa.get("artifacts") or [])
    try:
        from engines.voice_multimodal_learning.multimodal import interactive_bundle

        bundle = interactive_bundle(context)
    except Exception:  # noqa: BLE001
        bundle = {
            "math": {"engine_refs": ["engines.graphs", "engines.geometry.geogebra", "sympy"]},
            "physics": {"engine_refs": ["engines.physics", "engines.circuits"]},
            "chemistry": {"engine_refs": ["engines.chemistry"], "policy": "never_replace_deterministic"},
            "biology": {"engine_refs": ["ncert_figures", "verified_diagrams"]},
        }
    return {
        "ok": True,
        "verified_artifacts": artifacts[:20],
        "mathematics": bundle.get("math") or bundle.get("mathematics"),
        "physics": bundle.get("physics"),
        "chemistry": bundle.get("chemistry"),
        "biology": {
            "capabilities": ["zoom", "labels", "hotspots", "animations_when_available"],
            "prefer": "verified_ncert_diagrams",
        },
        "policy": "deterministic_engines_only_never_ai_invent_diagrams",
    }
