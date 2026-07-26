"""Optional VLIE-compatible engine wrapper for MIP (not auto-registered in VLIE)."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineResultBundle
from engines.mathematics_intelligence.service import analyse_mathematics_lesson, pack_health
from engines.universal_lesson_intelligence import (
    UniversalLessonIntelligence,
    build_universal_lesson_intelligence,
)


class MathematicsIntelligenceEngine(BaseEngine):
    """
    Opt-in Teaching-layer engine. Prefer SIF registry path via ULI pipeline.

    Does not replace ``engines.mathematics`` Computation Layer.
    """

    engine_id = "mathematics_intelligence"
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
                    errors=["MIP requires universal_lesson_intelligence or source_envelope"],
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
        analysis = analyse_mathematics_lesson(uli, context=context)
        return EngineResultBundle(
            engine_id=self.engine_id,
            ok=analysis.ok,
            payload={
                "mathematics_intelligence": analysis.to_dict(),
                "health": pack_health(),
            },
            warnings=list(analysis.warnings),
            deterministic=True,
        )
