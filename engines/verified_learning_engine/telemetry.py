"""Orchestration telemetry — latency, throughput, session metrics."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any
import time


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class TelemetryCollector:
    def __init__(self) -> None:
        self.engine_latencies_ms: dict[str, list[float]] = defaultdict(list)
        self.workflow_durations_ms: list[float] = []
        self.intervention_counts: dict[str, int] = defaultdict(int)
        self.event_counts: dict[str, int] = defaultdict(int)
        self.session_durations_s: list[float] = []
        self._timers: dict[str, float] = {}

    def start_timer(self, key: str) -> None:
        self._timers[key] = time.perf_counter()

    def stop_timer(self, key: str) -> float:
        start = self._timers.pop(key, None)
        if start is None:
            return 0.0
        ms = (time.perf_counter() - start) * 1000.0
        if key.startswith("engine:"):
            eid = key.split(":", 1)[1]
            self.engine_latencies_ms[eid].append(ms)
        elif key.startswith("workflow:"):
            self.workflow_durations_ms.append(ms)
        return ms

    def record_event(self, event_type: str) -> None:
        self.event_counts[event_type] += 1

    def record_intervention(self, kind: str) -> None:
        self.intervention_counts[kind] += 1

    def record_session_duration(self, seconds: float) -> None:
        self.session_durations_s.append(seconds)

    def snapshot(self) -> dict[str, Any]:
        def avg(vals: list[float]) -> float:
            return round(sum(vals) / len(vals), 2) if vals else 0.0

        return {
            "ts": _now(),
            "event_throughput": dict(self.event_counts),
            "engine_latency_avg_ms": {k: avg(v) for k, v in self.engine_latencies_ms.items()},
            "workflow_duration_avg_ms": avg(self.workflow_durations_ms),
            "intervention_frequency": dict(self.intervention_counts),
            "session_duration_avg_s": avg(self.session_durations_s),
            "resource_usage": {"note": "process-level metrics left to host monitoring"},
        }
