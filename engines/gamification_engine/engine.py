"""Gamification facade — delegates to LMAS for back-compat with ALCIS/LAIE."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth, EngineResultBundle


class GamificationEngine(BaseEngine):
    """
    VLIE id remains `gamification` for existing consumers.

    Full motivation economy lives in `engines/learning_motivation_engine` (LMAS).
    If LMAS already ran in this context, mirror its payload; otherwise build it.
    """

    engine_id = "gamification"
    version = "1.0.0"
    layer = "insight"
    priority = 80

    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        try:
            outputs = context.get("engine_outputs") or {}
            prior = outputs.get("learning_motivation") or {}
            if isinstance(prior, dict) and prior.get("payload"):
                payload = dict(prior["payload"])
            else:
                from engines.learning_motivation_engine.intelligence import build_motivation_payload

                payload = build_motivation_payload(context)
            # Ensure legacy shape keys
            payload.setdefault("enabled", True)
            payload.setdefault("design", "accessibility-first intrinsic motivation")
            return EngineResultBundle(engine_id=self.engine_id, ok=True, payload=payload, deterministic=True)
        except Exception as exc:  # noqa: BLE001
            return EngineResultBundle(engine_id=self.engine_id, ok=False, errors=[str(exc)])

    def health_check(self) -> EngineHealth:
        try:
            from engines.learning_motivation_engine.schemas import POLICY

            return EngineHealth(
                ok=True,
                engine_id=self.engine_id,
                version=self.version,
                detail=f"lmas_facade; no_public_leaderboards={POLICY['no_public_competitive_leaderboards']}",
                dependencies={"learning_motivation": True},
            )
        except Exception as exc:  # noqa: BLE001
            return EngineHealth(ok=False, engine_id=self.engine_id, detail=str(exc))
