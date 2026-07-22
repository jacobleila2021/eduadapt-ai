"""Optional VLIE-compatible engine wrapper for UVIE (not auto-registered)."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineResultBundle
from engines.universal_visual_intelligence.service import pack_health, render_visuals_for_uli


class UniversalVisualIntelligenceEngine(BaseEngine):
    engine_id = "universal_visual_intelligence"
    version = "1.0.0"
    layer = "computation"
    priority = 45

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        uli = context.get("universal_lesson_intelligence")
        result = render_visuals_for_uli(uli, context=context)
        assets: list[str] = []
        for vis in result.get("preferred_visuals") or []:
            if isinstance(vis, dict):
                assets.extend(str(p) for p in (vis.get("asset_paths") or []))
        return EngineResultBundle(
            engine_id=self.engine_id,
            ok=bool(result.get("ok")),
            payload={"universal_visual_intelligence": result, "health": pack_health()},
            assets=assets,
            warnings=[],
            deterministic=True,
        )
