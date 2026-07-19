"""Assessment & Mastery Engine — VLIE facade over official bank + AME intelligence.

Wraps question_bank / question_rag. Does not invent answer keys.
Integrates CIE bindings when curriculum stage has run.
"""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class AssessmentEngine(BaseEngine):
    engine_id = "assessment"
    version = "2.0.0"
    layer = "knowledge"
    priority = 30

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.assessment_mastery_engine.intelligence import analyze_assessment_context

            payload = analyze_assessment_context(context)
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=True,
                payload=payload,
                deterministic=True,
                warnings=[],
            )
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)])

    def health_check(self) -> EngineHealth:
        try:
            from knowledge.question_bank import load_official_items
            from engines.assessment_mastery_engine.misconceptions import list_misconceptions

            n = len(load_official_items())
            m = len(list_misconceptions())
            return EngineHealth(
                ok=n > 0,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"{n} official items; {m} misconceptions",
                dependencies={"question_bank": n > 0, "ame_misconceptions": m > 0},
            )
        except Exception as exc:
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
