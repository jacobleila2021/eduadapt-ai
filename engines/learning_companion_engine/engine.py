"""AI Learning Companion Intelligence System — VLIE facade (motivational layer)."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class LearningCompanionEngine(BaseEngine):
    """
    ALCIS — trust, confidence, motivation, engagement.

    Never teaches. ATIE remains teaching intelligence.
    """

    engine_id = "learning_companion"
    version = "1.0.0"
    layer = "teaching"
    priority = 78  # after LAIE planning hooks / near gamification

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.learning_companion_engine.companion_manager import analyze_companion_context

            payload = analyze_companion_context(context)
            return EngineResultBundle(engine_id=self.engine_id, ok=True, payload=payload, deterministic=False)
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)])

    def health_check(self) -> EngineHealth:
        try:
            from engines.learning_companion_engine.schemas import COMPANION_LIBRARY, PERSONALITY_STYLES

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"companions={len(COMPANION_LIBRARY)}; styles={len(PERSONALITY_STYLES)}; never_teaches",
                dependencies={"ai_tutor": True, "accessibility": True, "gamification": True, "voice_multimodal": True},
            )
        except Exception as exc:  # noqa: BLE001
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
