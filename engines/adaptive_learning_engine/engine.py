"""Adaptive Learning Engine — VLIE decision facade (does not generate lessons).

Consumes CIE / AME / AIE. Every decision is explainable and teacher-overridable.
"""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class AdaptiveLearningEngine(BaseEngine):
    engine_id = "adaptive_learning"
    version = "2.0.0"
    layer = "teaching"
    priority = 50

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.adaptive_learning_engine.intelligence import analyze_adaptive_context

            payload = analyze_adaptive_context(context)
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
            from engines.adaptive_learning_engine.schemas import DIFFICULTY_LEVELS, PATHWAY_TYPES

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"pathways={len(PATHWAY_TYPES)}; difficulties={len(DIFFICULTY_LEVELS)}; explainable",
                dependencies={"cie": True, "ame": True, "aie": True},
            )
        except Exception as exc:
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
