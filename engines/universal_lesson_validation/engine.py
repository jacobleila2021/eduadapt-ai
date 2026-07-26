"""VLIE-compatible engine wrapper for ULIQE (opt-in; not auto-registered)."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineResultBundle
from engines.universal_lesson_intelligence import build_universal_lesson_intelligence
from engines.universal_lesson_validation.service import validate_uli


class UniversalLessonValidationEngine(BaseEngine):
    """
    Optional VLIE plug-in. Not registered in engine_manager by default so
    existing orchestration remains unchanged (Milestone constraint).

    Expects context keys:
      - universal_lesson_intelligence OR (source_envelope + universal_profile)
      - optional stem_metadata / classifications
    """

    engine_id = "universal_lesson_validation"
    version = "1.0.0"
    layer = "qa"
    priority = 95

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        uli = context.get("universal_lesson_intelligence")
        if uli is None:
            envelope = context.get("source_envelope") or {}
            profile = context.get("universal_profile")
            if not envelope:
                return EngineResultBundle(
                    engine_id=self.engine_id,
                    ok=False,
                    errors=["ULIQE requires universal_lesson_intelligence or source_envelope"],
                    deterministic=True,
                )
            uli = build_universal_lesson_intelligence(
                envelope,
                profile,
                stem_metadata=context.get("stem_metadata"),
                classifications=context.get("classifications"),
            )
        report = validate_uli(uli)
        return EngineResultBundle(
            engine_id=self.engine_id,
            ok=report.ok,
            payload={
                "uliqe": report.to_dict(),
                "downstream_allowed": report.downstream_allowed,
                "certification": report.certification.value,
            },
            errors=[
                f.message
                for f in report.findings
                if f.severity.value in {"error", "critical"}
            ][:20],
            warnings=report.warnings[:30],
            deterministic=True,
        )
