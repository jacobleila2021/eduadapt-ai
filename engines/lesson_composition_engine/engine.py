"""Lesson Composition Engine — VLIE teaching-layer facade.

Owns educational writing. Never invents curriculum or alters EngineResult payloads.
"""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class LessonCompositionEngine(BaseEngine):
    engine_id = "lesson_composition"
    version = "1.0.0"
    layer = "teaching"
    priority = 70

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            from engines.lesson_composition_engine.composer import compose_lesson_package

            uli = context.get("uli") or {
                "universal_profile": context.get("universal_profile") or {},
                "claim_ledger": (context.get("universal_profile") or {}).get("claim_ledger")
                or context.get("claim_ledger")
                or [],
            }
            sif = context.get("sif") or {}
            uvie = context.get("uvie") or {
                "visuals": context.get("preferred_visuals") or [],
                "preferred_visuals": context.get("preferred_visuals") or [],
            }
            result = compose_lesson_package(
                uli,
                sif=sif,
                uvie=uvie,
                topic_hint=str(context.get("topic") or ""),
            )
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=bool(result.get("ok")),
                payload={
                    **result,
                    "policy": result.get("policy")
                    or {
                        "composes_lessons": True,
                        "does_not_invent_curriculum": True,
                        "reuses": ["uli", "sif", "uvie", "subject_packs", "aie"],
                    },
                },
                warnings=[] if result.get("ok") else ["lce_eerl_not_ready"],
                deterministic=True,
            )
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(
                engine_id=self.engine_id,
                ok=False,
                errors=[str(exc)],
            )

    def health_check(self) -> EngineHealth:
        try:
            from engines.lesson_composition_engine.schemas import (
                ADAPTIVE_VERSION_IDS,
                PACK_VERSION,
                QUALITY_CATEGORIES,
            )

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=(
                    f"schema={PACK_VERSION}; "
                    f"versions={len(ADAPTIVE_VERSION_IDS)}; "
                    f"gates={len(QUALITY_CATEGORIES)}; clg+eerl"
                ),
                dependencies={
                    "uli": True,
                    "sif": True,
                    "uvie": True,
                    "accessibility": True,
                },
            )
        except Exception as exc:  # noqa: BLE001
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
