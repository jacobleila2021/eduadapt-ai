"""Curriculum Migration & Ingestion Framework — VLIE facade."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class CurriculumMigrationEngine(BaseEngine):
    """
    CMIF — production curriculum import → UCF.

    Reuses KIE parsers, CEF mapping/publish, UCF schema.
    Never generates curriculum with AI. Never bypasses the mandatory pipeline.
    """

    engine_id = "curriculum_migration"
    version = "1.0.0"
    layer = "knowledge"
    priority = 9  # alongside curriculum_expansion; after UCF (8)

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.curriculum_migration_framework.dashboard import admin_dashboard
            from engines.curriculum_migration_framework.schemas import PIPELINE_STAGES, SUPPORTED_BOARDS

            payload: dict[str, Any] = {
                "system": "CMIF",
                "schema_target": "ucf/1.0",
                "pipeline_stages": list(PIPELINE_STAGES),
                "supported_boards": list(SUPPORTED_BOARDS),
                "policy": {
                    "never_generate_curriculum_with_ai": True,
                    "engines_consume_ucf_only": True,
                    "pipeline_mandatory": True,
                    "immutable_published": True,
                    "reuse": ["kie", "ucf", "cef"],
                },
            }
            if context.get("inline") or context.get("path"):
                from engines.curriculum_migration_framework.migration import run_migration

                payload["migration"] = run_migration(
                    board=str(context.get("board") or "cbse"),
                    path=str(context.get("path") or ""),
                    inline=context.get("inline"),
                    source_url=str(context.get("source_url") or "cmif://vlie"),
                    publish=bool(context.get("publish", False)),
                    role=str(context.get("role") or "system"),
                    lazy_index=bool(context.get("lazy_index", True)),
                )
            if context.get("include_dashboard"):
                payload["dashboard"] = admin_dashboard()
            return EngineResultBundle(engine_id=self.engine_id, ok=True, payload=payload, deterministic=True)
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)])

    def health_check(self) -> EngineHealth:
        try:
            from engines.curriculum_migration_framework.schemas import PIPELINE_STAGES, SUPPORTED_BOARDS

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"stages={len(PIPELINE_STAGES)}; boards={len(SUPPORTED_BOARDS)}; target=ucf/1.0",
                dependencies={"universal_curriculum": True, "knowledge_ingestion": True, "curriculum_expansion": True},
            )
        except Exception as exc:  # noqa: BLE001
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
