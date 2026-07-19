"""Learning Motivation & Achievement System — VLIE facade."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class LearningMotivationEngine(BaseEngine):
    """
    LMAS — meaningful progression & recognition.

    Does not alter curriculum or assessment. Intrinsic motivation first.
    """

    engine_id = "learning_motivation"
    version = "1.0.0"
    layer = "insight"
    priority = 79  # just before legacy gamification facade (80)

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.learning_motivation_engine.intelligence import build_motivation_payload

            payload = build_motivation_payload(context)
            return EngineResultBundle(engine_id=self.engine_id, ok=True, payload=payload, deterministic=True)
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)])

    def health_check(self) -> EngineHealth:
        try:
            from engines.learning_motivation_engine.schemas import LEVELS, POLICY

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"levels={len(LEVELS)}; intrinsic_first={POLICY['intrinsic_before_extrinsic']}",
                dependencies={"curriculum": True, "assessment": True, "accessibility": True, "adaptive_learning": True},
            )
        except Exception as exc:  # noqa: BLE001
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
