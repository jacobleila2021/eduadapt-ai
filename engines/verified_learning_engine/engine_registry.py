"""Engine registry — plug-and-play registration, health, feature flags."""

from __future__ import annotations

from typing import Any

from engines.base import BaseEngine, EngineHealth


class EngineRegistry:
    def __init__(self) -> None:
        self._engines: dict[str, BaseEngine] = {}
        self._enabled: dict[str, bool] = {}
        self._versions: dict[str, str] = {}
        self._dependencies: dict[str, list[str]] = {}

    def register(
        self,
        engine: BaseEngine,
        *,
        enabled: bool = True,
        depends_on: list[str] | None = None,
    ) -> None:
        engine.initialize()
        self._engines[engine.engine_id] = engine
        self._enabled[engine.engine_id] = enabled
        self._versions[engine.engine_id] = engine.version
        self._dependencies[engine.engine_id] = depends_on or []

    def unregister(self, engine_id: str) -> None:
        self._engines.pop(engine_id, None)
        self._enabled.pop(engine_id, None)
        self._versions.pop(engine_id, None)
        self._dependencies.pop(engine_id, None)

    def get(self, engine_id: str) -> BaseEngine | None:
        return self._engines.get(engine_id)

    def enable(self, engine_id: str) -> None:
        if engine_id in self._enabled:
            self._enabled[engine_id] = True

    def disable(self, engine_id: str) -> None:
        if engine_id in self._enabled:
            self._enabled[engine_id] = False

    def is_enabled(self, engine_id: str) -> bool:
        return bool(self._enabled.get(engine_id, False))

    def list_engines(self) -> list[dict[str, Any]]:
        rows = []
        for eid, eng in sorted(self._engines.items(), key=lambda x: x[1].priority):
            rows.append(
                {
                    "engine_id": eid,
                    "version": self._versions.get(eid),
                    "enabled": self._enabled.get(eid, False),
                    "layer": eng.layer,
                    "priority": eng.priority,
                    "depends_on": self._dependencies.get(eid, []),
                }
            )
        return rows

    def health_all(self) -> list[EngineHealth]:
        return [e.health_check() for e in self._engines.values()]

    def execution_order(self, only_enabled: bool = True) -> list[BaseEngine]:
        """Return a stable topological order, using priority only as a tie-breaker."""
        selected = {
            eid
            for eid in self._engines
            if not only_enabled or self._enabled.get(eid, False)
        }
        missing: list[str] = []
        disabled: list[str] = []
        for eid in selected:
            for dep in self._dependencies.get(eid, []):
                if dep not in self._engines:
                    missing.append(f"{eid}->{dep}")
                elif only_enabled and dep not in selected:
                    disabled.append(f"{eid}->{dep}")
        if missing:
            raise RuntimeError(f"Missing engine dependencies: {', '.join(sorted(missing))}")
        if disabled:
            raise RuntimeError(f"Required engine dependencies are disabled: {', '.join(sorted(disabled))}")

        ordered: list[BaseEngine] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(eid: str, path: list[str]) -> None:
            if eid in visited:
                return
            if eid in visiting:
                cycle = " -> ".join(path + [eid])
                raise RuntimeError(f"Engine dependency cycle: {cycle}")
            visiting.add(eid)
            dependencies = [
                dep for dep in self._dependencies.get(eid, []) if dep in selected
            ]
            dependencies.sort(key=lambda dep: (self._engines[dep].priority, dep))
            for dep in dependencies:
                visit(dep, path + [eid])
            visiting.remove(eid)
            visited.add(eid)
            ordered.append(self._engines[eid])

        roots = sorted(
            selected, key=lambda eid: (self._engines[eid].priority, eid)
        )
        for eid in roots:
            visit(eid, [])
        return ordered


_GLOBAL_REGISTRY: EngineRegistry | None = None


def get_registry() -> EngineRegistry:
    global _GLOBAL_REGISTRY
    if _GLOBAL_REGISTRY is None:
        _GLOBAL_REGISTRY = EngineRegistry()
        from engines.verified_learning_engine.engine_manager import register_default_engines

        register_default_engines(_GLOBAL_REGISTRY)
    return _GLOBAL_REGISTRY


def reset_registry() -> EngineRegistry:
    global _GLOBAL_REGISTRY
    _GLOBAL_REGISTRY = EngineRegistry()
    from engines.verified_learning_engine.engine_manager import register_default_engines

    register_default_engines(_GLOBAL_REGISTRY)
    return _GLOBAL_REGISTRY
