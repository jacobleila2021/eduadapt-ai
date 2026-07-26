"""Optional VLIE-compatible engine wrapper (not auto-registered)."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineResultBundle
from engines.subject_intelligence_framework.service import enrich_uli_with_subject_intelligence
from engines.universal_lesson_intelligence import (
    UniversalLessonIntelligence,
    build_universal_lesson_intelligence,
)


class SubjectIntelligenceFrameworkEngine(BaseEngine):
    """
    Opt-in VLIE plug-in. Not registered in engine_manager by default.

    Expects ``universal_lesson_intelligence`` or envelope+profile in context.
    """

    engine_id = "subject_intelligence_framework"
    version = "1.0.0"
    layer = "teaching"
    priority = 55

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        uli = context.get("universal_lesson_intelligence")
        if uli is None:
            envelope = context.get("source_envelope") or {}
            if not envelope:
                return EngineResultBundle(
                    engine_id=self.engine_id,
                    ok=False,
                    errors=["SIF requires universal_lesson_intelligence or source_envelope"],
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
        payload = enrich_uli_with_subject_intelligence(
            uli,
            subject_key=context.get("subject_key"),
            context=context,
        )
        return EngineResultBundle(
            engine_id=self.engine_id,
            ok=True,
            payload={"sif": payload},
            warnings=list((payload.get("analysis") or {}).get("warnings") or []),
            deterministic=True,
        )
