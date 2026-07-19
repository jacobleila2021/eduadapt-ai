"""Retry & recovery for engine calls and session restoration."""

from __future__ import annotations

from typing import Any, Callable
import time


class RetryManager:
    def __init__(self, *, max_attempts: int = 3, base_delay_s: float = 0.05, timeout_s: float = 30.0) -> None:
        self.max_attempts = max_attempts
        self.base_delay_s = base_delay_s
        self.timeout_s = timeout_s
        self.failures: list[dict[str, Any]] = []

    def call(
        self,
        fn: Callable[[], Any],
        *,
        label: str = "op",
        fallback: Any = None,
    ) -> dict[str, Any]:
        last_err: Exception | None = None
        for attempt in range(1, self.max_attempts + 1):
            try:
                result = fn()
                return {"ok": True, "result": result, "attempts": attempt, "label": label}
            except Exception as exc:  # noqa: BLE001
                last_err = exc
                self.failures.append({"label": label, "attempt": attempt, "error": str(exc)})
                if attempt < self.max_attempts:
                    time.sleep(self.base_delay_s * attempt)
        return {
            "ok": False,
            "result": fallback,
            "attempts": self.max_attempts,
            "label": label,
            "error": str(last_err) if last_err else "unknown",
            "fallback_used": fallback is not None,
        }

    def export_failures(self) -> list[dict[str, Any]]:
        return list(self.failures)
