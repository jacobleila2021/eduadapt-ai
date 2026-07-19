"""AI Tutor Engine — VLIE facade over ATIE (curriculum-grounded tutoring).

Never invents curriculum, STEM facts, or official answers.
"""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class AITutorEngine(BaseEngine):
    engine_id = "ai_tutor"
    version = "2.0.0"
    layer = "teaching"
    priority = 60

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.ai_tutor_intelligence_engine.intelligence import analyze_tutor_context

            payload = analyze_tutor_context(context)
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=True,
                payload=payload,
                deterministic=True,
                warnings=[] if payload.get("grounding_packet", {}).get("ok", True) else ["insufficient_verified_evidence"],
            )
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)])

    def health_check(self) -> EngineHealth:
        try:
            from engines.ai_tutor_intelligence_engine.schemas import TUTOR_MODES

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"modes={len(TUTOR_MODES)}; grounded retrieval; audio_learning",
                dependencies={"cie": True, "ame": True, "aie": True, "ale": True, "stem": True},
            )
        except Exception as exc:
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
