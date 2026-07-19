"""Health monitoring for registered engines and orchestration queues."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from engines.verified_learning_engine.engine_registry import EngineRegistry, get_registry
from engines.verified_learning_engine.dependency_manager import DependencyManager


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class HealthMonitor:
    def __init__(self, registry: EngineRegistry | None = None) -> None:
        self.registry = registry or get_registry()
        self.alerts: list[dict[str, Any]] = []
        self.failure_counts: dict[str, int] = {}

    def record_failure(self, engine_id: str) -> None:
        self.failure_counts[engine_id] = self.failure_counts.get(engine_id, 0) + 1
        if self.failure_counts[engine_id] >= 3:
            self.alerts.append(
                {
                    "ts": _now(),
                    "severity": "high",
                    "engine_id": engine_id,
                    "message": f"Repeated failures for {engine_id}",
                }
            )

    def report(self, *, queue_length: int = 0, telemetry: dict[str, Any] | None = None) -> dict[str, Any]:
        engines = []
        for row in self.registry.list_engines():
            eid = row["engine_id"]
            engines.append(
                {
                    "engine_id": eid,
                    "enabled": row.get("enabled"),
                    "version": row.get("version"),
                    "health": "degraded" if self.failure_counts.get(eid, 0) else "ok",
                    "failures": self.failure_counts.get(eid, 0),
                }
            )
        dep = DependencyManager(self.registry).validate_no_cycles()
        report = {
            "ts": _now(),
            "overall": "ok" if dep.get("ok") and not self.alerts else "degraded",
            "engines": engines,
            "dependency_status": dep,
            "queue_length": queue_length,
            "processing_failures": dict(self.failure_counts),
            "latency": (telemetry or {}).get("engine_latency_avg_ms") or {},
            "alerts": list(self.alerts[-20:]),
        }
        return report
