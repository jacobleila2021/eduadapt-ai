"""Engine dependency order — wraps registry; prevents cycles."""

from __future__ import annotations

from typing import Any

from engines.verified_learning_engine.engine_registry import EngineRegistry, get_registry

# Canonical educational dependency chain (documentation + validation)
CANONICAL_CHAIN = (
    "knowledge_ingestion",
    "universal_curriculum",
    "curriculum_expansion",
    "curriculum_migration",
    "curriculum",
    "assessment",
    "accessibility",
    "adaptive_learning",
    "ai_tutor",
    "voice_multimodal",
    "learning_experience",
    "learning_analytics",
    "learning_motivation",
    "gamification",
    "learning_companion",
    "quality_assurance",
)


class DependencyManager:
    def __init__(self, registry: EngineRegistry | None = None) -> None:
        self.registry = registry or get_registry()

    def execution_order(self, only_enabled: bool = True) -> list[str]:
        return [e.engine_id for e in self.registry.execution_order(only_enabled=only_enabled)]

    def validate_no_cycles(self) -> dict[str, Any]:
        deps = {}
        for row in self.registry.list_engines():
            deps[row["engine_id"]] = list(row.get("depends_on") or [])
        visiting: set[str] = set()
        visited: set[str] = set()
        cycles: list[list[str]] = []

        def dfs(node: str, path: list[str]) -> None:
            if node in visiting:
                cycles.append(path + [node])
                return
            if node in visited:
                return
            visiting.add(node)
            for nxt in deps.get(node, []):
                dfs(nxt, path + [node])
            visiting.remove(node)
            visited.add(node)

        for n in deps:
            dfs(n, [])
        return {"ok": not cycles, "cycles": cycles, "canonical_chain": list(CANONICAL_CHAIN)}

    def plan_for_workflow_step(self, engines: list[str]) -> list[str]:
        """Order requested engines by registry priority."""
        order = self.execution_order(only_enabled=False)
        rank = {eid: i for i, eid in enumerate(order)}
        return sorted(engines, key=lambda e: rank.get(e, 999))
