"""Universal Curriculum Framework — VLIE facade (schema layer, not a curriculum)."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class UniversalCurriculumEngine(BaseEngine):
    """
    UCF — one internal academic model for all boards.

    Does not replace CIE; CIE should consume UCF projections.
    """

    engine_id = "universal_curriculum"
    version = "1.0.0"
    layer = "knowledge"
    priority = 8  # after KIE (5), before CIE curriculum (10)

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.universal_curriculum_framework.intelligence import analyze_ucf_context

            payload = analyze_ucf_context(context)
            return EngineResultBundle(engine_id=self.engine_id, ok=True, payload=payload, deterministic=True)
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)])

    def health_check(self) -> EngineHealth:
        try:
            from engines.universal_curriculum_framework.board_registry import supported_board_names
            from engines.universal_curriculum_framework.schemas import TAXONOMIES

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"boards={len(supported_board_names())}; taxonomies={len(TAXONOMIES)}; schema=ucf/1.0",
                dependencies={"knowledge_ingestion": True},
            )
        except Exception as exc:  # noqa: BLE001
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
