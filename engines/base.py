"""Standard engine interface for Alora VLIE plug-and-play engines."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class EngineHealth:
    ok: bool
    engine_id: str
    version: str = "1.0.0"
    detail: str = ""
    dependencies: dict[str, bool] = field(default_factory=dict)


@dataclass
class EngineResultBundle:
    """Normalized output every engine returns to VLIE."""

    engine_id: str
    ok: bool
    payload: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    assets: list[str] = field(default_factory=list)
    deterministic: bool = False


class BaseEngine(ABC):
    """
    Contract for all VLIE-managed engines.

    Engines must not call each other directly — only VLIE coordinates.
    """

    engine_id: str = "base"
    version: str = "1.0.0"
    layer: str = "unknown"  # knowledge | computation | teaching | qa | insight
    priority: int = 100  # lower runs earlier

    def initialize(self, config: dict[str, Any] | None = None) -> None:
        self._config = config or {}

    @abstractmethod
    def process(self, context: dict[str, Any]) -> EngineResultBundle:
        ...

    def validate(self, context: dict[str, Any], result: EngineResultBundle) -> EngineResultBundle:
        return result

    def enrich(self, context: dict[str, Any], result: EngineResultBundle) -> EngineResultBundle:
        return result

    def export(self, result: EngineResultBundle) -> dict[str, Any]:
        return {
            "engine_id": result.engine_id,
            "ok": result.ok,
            "payload": result.payload,
            "errors": result.errors,
            "warnings": result.warnings,
            "assets": result.assets,
            "deterministic": result.deterministic,
        }

    def health_check(self) -> EngineHealth:
        return EngineHealth(ok=True, engine_id=self.engine_id, version=self.version)
