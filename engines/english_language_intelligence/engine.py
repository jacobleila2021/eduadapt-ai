"""Optional VLIE-compatible engine wrapper for ELIP (not auto-registered)."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineResultBundle
from engines.english_language_intelligence.service import analyse_english_lesson, pack_health
from engines.universal_lesson_intelligence import (
    UniversalLessonIntelligence,
    build_universal_lesson_intelligence,
)


class EnglishLanguageIntelligenceEngine(BaseEngine):
    engine_id = "english_language_intelligence"
    version = "1.0.0"
    layer = "teaching"
    priority = 56

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        uli = context.get("universal_lesson_intelligence")
        if uli is None:
            envelope = context.get("source_envelope") or {}
            if not envelope:
                return EngineResultBundle(
                    engine_id=self.engine_id,
                    ok=False,
                    errors=["ELIP requires universal_lesson_intelligence or source_envelope"],
                    deterministic=True,
                )
            uli = build_universal_lesson_intelligence(
                envelope,
                context.get("universal_profile"),
                stem_metadata=context.get("stem_metadata"),
                classifications=context.get("classifications"),
                enrich=bool(context.get("enrich", False)),
            )
        if not isinstance(uli, UniversalLessonIntelligence):
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=False,
                errors=["Invalid ULI object"],
                deterministic=True,
            )
        analysis = analyse_english_lesson(uli, context=context)
        return EngineResultBundle(
            engine_id=self.engine_id,
            ok=analysis.ok,
            payload={"english_language_intelligence": analysis.to_dict(), "health": pack_health()},
            warnings=list(analysis.warnings),
            deterministic=True,
        )
