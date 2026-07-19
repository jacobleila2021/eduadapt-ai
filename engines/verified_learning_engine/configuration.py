"""Central LSO configuration — workflows, flags, timeouts, retries, logging."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class LSOConfig:
    workflow_default: str = "lesson_learning"
    feature_flags: dict[str, bool] = field(
        default_factory=lambda: {
            "event_bus": True,
            "session_orchestration": True,
            "interventions": True,
            "scheduler": True,
            "notifications": True,
            "offline_sessions": True,
        }
    )
    timeouts_s: dict[str, float] = field(
        default_factory=lambda: {
            "engine_call": 30.0,
            "workflow_step": 120.0,
            "session_idle": 3600.0,
        }
    )
    retry: dict[str, Any] = field(
        default_factory=lambda: {"max_attempts": 3, "base_delay_s": 0.05}
    )
    event_subscriptions: list[str] = field(default_factory=lambda: ["*"])
    logging_level: str = "INFO"
    scheduler_intervals: dict[str, int] = field(
        default_factory=lambda: {
            "review_check_minutes": 15,
            "offline_sync_minutes": 5,
            "health_check_minutes": 1,
        }
    )

    def export(self) -> dict[str, Any]:
        return asdict(self)

    def flag(self, name: str, default: bool = False) -> bool:
        return bool(self.feature_flags.get(name, default))


_CONFIG: LSOConfig | None = None


def get_lso_config() -> LSOConfig:
    global _CONFIG
    if _CONFIG is None:
        _CONFIG = LSOConfig()
    return _CONFIG


def reset_lso_config() -> None:
    global _CONFIG
    _CONFIG = None
