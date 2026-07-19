"""Voice & Multimodal Learning Experience — VLIE facade (presentation layer)."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class VoiceMultimodalEngine(BaseEngine):
    """
    VMLE — speech, read-along, interactive STEM presentation.

    Does not replace ATIE (teaching), AIE (accessibility prefs), or STEM engines.
    """

    engine_id = "voice_multimodal"
    version = "1.0.0"
    layer = "teaching"
    priority = 65  # after ai_tutor (60); LAIE at 70 consumes multimodal usage

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.voice_multimodal_learning.intelligence import analyze_voice_multimodal_context

            payload = analyze_voice_multimodal_context(context)
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=True,
                payload=payload,
                deterministic=False,  # TTS timing estimates; STEM refs remain deterministic
            )
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)])

    def health_check(self) -> EngineHealth:
        try:
            from engines.voice_multimodal_learning.schemas import VOICE_COMMANDS
            from audio_learning import VOICE_OPTIONS

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"commands={len(VOICE_COMMANDS)}; voices={len(VOICE_OPTIONS)}; wraps audio_learning+atie",
                dependencies={"accessibility": True, "ai_tutor": True, "scientific_accuracy": True},
            )
        except Exception as exc:  # noqa: BLE001
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
