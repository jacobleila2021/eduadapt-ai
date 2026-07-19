"""Curriculum Expansion Framework — VLIE facade (multi-board → UCF)."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class CurriculumExpansionEngine(BaseEngine):
    """
    CEF — import/map/validate/version multi-board curricula into UCF.

    Does not replace UCF or CIE. Engines continue to consume UCF only.
    """

    engine_id = "curriculum_expansion"
    version = "1.0.0"
    layer = "knowledge"
    priority = 9  # after universal_curriculum (8), before CIE curriculum (10)

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.curriculum_expansion_framework.registry import ensure_family_catalogue, list_supported_boards
            from engines.curriculum_expansion_framework.dashboards import admin_dashboard

            ensure_family_catalogue()
            seed = context.get("seed_priority")
            seed_result = None
            if seed:
                from engines.curriculum_expansion_framework.service import api_seed_priority

                seed_result = api_seed_priority()

            payload = {
                "system": "CEF",
                "schema_target": "ucf/1.0",
                "supported_boards": list_supported_boards(),
                "dashboard": admin_dashboard() if context.get("include_dashboard") else None,
                "seed_result": seed_result,
                "policy": {
                    "engines_consume_ucf_only": True,
                    "no_board_branches_in_engines": True,
                    "incremental_population": True,
                    "priority_order": [
                        "ncert+cbse",
                        "icse/isc",
                        "cambridge",
                        "ib",
                        "kerala_scert",
                        "university",
                        "professional",
                    ],
                },
            }
            return EngineResultBundle(engine_id=self.engine_id, ok=True, payload=payload, deterministic=True)
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)])

    def health_check(self) -> EngineHealth:
        try:
            from engines.curriculum_expansion_framework.schemas import CURRICULUM_FAMILIES

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"families={len(CURRICULUM_FAMILIES)}; target=ucf/1.0; incremental=ncert+cbse_first",
                dependencies={"universal_curriculum": True, "knowledge_ingestion": True},
            )
        except Exception as exc:  # noqa: BLE001
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
