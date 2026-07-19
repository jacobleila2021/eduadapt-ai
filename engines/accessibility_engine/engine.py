"""Accessibility Intelligence Engine — VLIE facade (presentation only).

Wraps adaptation_specs + AIE. Never alters curriculum facts or official answers.
"""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class AccessibilityEngine(BaseEngine):
    engine_id = "accessibility"
    version = "2.0.0"
    layer = "teaching"
    priority = 40

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.accessibility_intelligence_engine.intelligence import (
                analyze_accessibility_context,
            )

            payload = analyze_accessibility_context(context)
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=True,
                payload=payload,
                deterministic=True,
            )
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)])

    def health_check(self) -> EngineHealth:
        try:
            from adaptation_specs import ADAPTATION_SPECS
            from engines.accessibility_intelligence_engine.sensory_profiles import catalog

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"specs={len(ADAPTATION_SPECS)}; profiles={len(catalog())}; WCAG 2.2 AA",
                dependencies={"adaptation_specs": True, "aie": True},
            )
        except Exception as exc:
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
