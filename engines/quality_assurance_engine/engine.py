"""Quality Assurance Engine — facade over engines.qa + chapter cache."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class QualityAssuranceEngine(BaseEngine):
    engine_id = "quality_assurance"
    version = "1.0.0"
    layer = "qa"
    priority = 100

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.qa.pipeline import validate_lesson_package

            stem = (context.get("engine_outputs") or {}).get("scientific_accuracy") or {}
            payload = stem.get("payload") or {}
            curr = (context.get("engine_outputs") or {}).get("curriculum") or {}
            knowledge = (curr.get("payload") or {}).get("knowledge") or {}
            assess = (context.get("engine_outputs") or {}).get("assessment") or {}
            if assess.get("payload"):
                knowledge = {
                    **knowledge,
                    "official_mcqs": assess["payload"].get("official_mcqs") or knowledge.get("official_mcqs"),
                    "exam_bundle": assess["payload"].get("exam_bundle") or knowledge.get("exam_bundle"),
                }

            report = validate_lesson_package(
                artifacts=payload.get("artifacts") or [],
                preferred_visuals=payload.get("preferred_visuals") or [],
                knowledge=knowledge,
                adaptations=context.get("adaptations"),
            )
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=report.passed and not report.publish_blocked,
                payload={
                    "passed": report.passed,
                    "publish_blocked": report.publish_blocked,
                    "blocked_reason": report.blocked_reason,
                    "checks": report.checks,
                    "scorecard": getattr(report, "scorecard", {}) or {},
                },
                errors=[report.blocked_reason] if report.publish_blocked else [],
                deterministic=True,
            )
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)], deterministic=True)

    def health_check(self) -> EngineHealth:
        return EngineHealth(ok=True, engine_id=self.engine_id, detail="engines.qa.pipeline + chapter_cache")
