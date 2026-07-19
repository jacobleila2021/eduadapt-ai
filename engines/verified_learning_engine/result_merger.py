"""Merge engine outputs into a single context map for VLIE."""

from __future__ import annotations

from typing import Any

from engines.base import EngineResultBundle


class ResultMerger:
    def merge(
        self,
        engine_outputs: dict[str, EngineResultBundle],
    ) -> dict[str, Any]:
        merged: dict[str, Any] = {
            "ok": all(r.ok for r in engine_outputs.values()) if engine_outputs else True,
            "engines": {},
            "deterministic_assets": [],
            "errors": [],
            "warnings": [],
        }
        for eid, result in engine_outputs.items():
            merged["engines"][eid] = {
                "ok": result.ok,
                "payload": result.payload,
                "deterministic": result.deterministic,
                "assets": result.assets,
            }
            merged["deterministic_assets"].extend(result.assets)
            merged["errors"].extend(result.errors)
            merged["warnings"].extend(result.warnings)
        return merged
