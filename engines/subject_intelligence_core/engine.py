"""Optional VLIE-compatible wrapper for SICS (not auto-registered)."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineResultBundle
from engines.subject_intelligence_core.service import core_health, demo_capabilities


class SubjectIntelligenceCoreEngine(BaseEngine):
    """Exposes core health / capability catalogue for diagnostics."""

    engine_id = "subject_intelligence_core"
    version = "1.0.0"
    layer = "teaching"
    priority = 50

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        _ = context
        return EngineResultBundle(
            engine_id=self.engine_id,
            ok=True,
            payload={"sics": demo_capabilities(), "health": core_health()},
            deterministic=True,
        )
