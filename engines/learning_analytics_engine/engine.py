"""Learning Analytics & Insights Engine — VLIE facade (insights only).

Wraps analytics_engine.py and consumes CIE/AME/AIE/ALE.
Never mutates curriculum, answers, or accessibility decisions.
"""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class LearningAnalyticsEngine(BaseEngine):
    engine_id = "learning_analytics"
    version = "2.0.0"
    layer = "insight"
    priority = 70

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.learning_analytics_engine.intelligence import analyze_insights

            payload = analyze_insights(context)
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=True,
                payload=payload,
                deterministic=True,
            )
        except Exception as exc:  # noqa: BLE001
            # Soft-fail like v1 — never block lesson pipeline
            try:
                from analytics_engine import build_analytics_report

                report = build_analytics_report(context.get("lesson_text") or "")
            except Exception:
                report = {}
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=True,
                warnings=[str(exc)],
                payload={"report": report, "note": "laie soft-failed; lesson report only"},
            )

    def health_check(self) -> EngineHealth:
        try:
            import analytics_engine  # noqa: F401
            from engines.learning_analytics_engine.schemas import ROLES

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"roles={len(ROLES)}; wraps analytics_engine + CIE/AME/AIE/ALE",
                dependencies={"analytics_engine": True, "ale": True, "ame": True},
            )
        except Exception as exc:
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
