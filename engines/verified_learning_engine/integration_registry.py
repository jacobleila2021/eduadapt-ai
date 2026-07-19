"""Integration registry — plug-in engines without changing VLIE core."""

from __future__ import annotations

from typing import Any

from engines.verified_learning_engine.engine_registry import EngineRegistry, get_registry


class IntegrationRegistry:
    """
    Declares connected engines: name, version, dependencies, health,
    capabilities, API endpoints. Future engines register here.
    """

    def __init__(self, registry: EngineRegistry | None = None) -> None:
        self.registry = registry or get_registry()
        self._extras: dict[str, dict[str, Any]] = {}
        self._planned: dict[str, dict[str, Any]] = {}

    def register_capability(
        self,
        engine_id: str,
        *,
        capabilities: list[str] | None = None,
        api_endpoints: list[str] | None = None,
        health: str = "ok",
    ) -> dict[str, Any]:
        meta = self._extras.setdefault(engine_id, {})
        if capabilities is not None:
            meta["capabilities"] = capabilities
        if api_endpoints is not None:
            meta["api_endpoints"] = api_endpoints
        meta["health"] = health
        return self.describe(engine_id)

    def describe(self, engine_id: str) -> dict[str, Any]:
        row = next((e for e in self.registry.list_engines() if e["engine_id"] == engine_id), None)
        if row:
            extra = self._extras.get(engine_id) or {}
            eng = self.registry.get(engine_id)
            return {
                "name": getattr(eng, "name", None) or engine_id,
                "engine_id": engine_id,
                "version": row.get("version"),
                "dependencies": row.get("depends_on") or [],
                "health_status": extra.get("health") or ("ok" if row.get("enabled") else "disabled"),
                "supported_capabilities": extra.get("capabilities")
                or list(getattr(eng, "capabilities", ()) or ()),
                "api_endpoints": extra.get("api_endpoints") or [],
                "enabled": row.get("enabled"),
                "registered": True,
            }
        planned = self._planned.get(engine_id)
        if planned:
            return {**planned, "registered": False, "planned": True}
        return {"engine_id": engine_id, "registered": False}

    def list_all(self) -> list[dict[str, Any]]:
        ids = {e["engine_id"] for e in self.registry.list_engines()} | set(self._planned)
        return [self.describe(eid) for eid in sorted(ids)]

    def register_future_engine(
        self,
        engine_id: str,
        *,
        name: str,
        version: str = "0.1.0",
        depends_on: list[str] | None = None,
        capabilities: list[str] | None = None,
        api_endpoints: list[str] | None = None,
        enabled: bool = False,
    ) -> dict[str, Any]:
        """Reserve a slot for engines not yet implemented (Voice, Companion, etc.)."""
        self._planned[engine_id] = {
            "name": name,
            "engine_id": engine_id,
            "version": version,
            "dependencies": list(depends_on or []),
            "health_status": "planned",
            "supported_capabilities": list(capabilities or []),
            "api_endpoints": list(api_endpoints or []),
            "enabled": enabled,
        }
        return self.describe(engine_id)
