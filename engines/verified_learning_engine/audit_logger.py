"""Append-only audit trail for VLIE runs and orchestration decisions."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class AuditLogger:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def log(self, event: str, **payload: Any) -> None:
        self.events.append(
            {
                "ts": datetime.now(timezone.utc).isoformat(),
                "event": event,
                **payload,
            }
        )

    def log_decision(
        self,
        *,
        learner: str = "",
        lesson: str = "",
        event: str = "",
        engine: str = "",
        decision: str = "",
        reason: str = "",
        confidence: float | None = None,
        evidence: list[Any] | None = None,
        session_id: str = "",
    ) -> dict[str, Any]:
        row = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": "orchestration_decision",
            "learner": learner,
            "lesson": lesson,
            "trigger_event": event,
            "engine": engine,
            "decision": decision,
            "reason": reason,
            "confidence": confidence,
            "evidence": evidence or [],
            "session_id": session_id,
        }
        self.events.append(row)
        return row

    def search(
        self,
        *,
        session_id: str | None = None,
        learner: str | None = None,
        event: str | None = None,
        engine: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        rows = self.events
        if session_id:
            rows = [e for e in rows if e.get("session_id") == session_id]
        if learner:
            rows = [e for e in rows if e.get("learner") == learner]
        if event:
            rows = [e for e in rows if e.get("event") == event or e.get("trigger_event") == event]
        if engine:
            rows = [e for e in rows if e.get("engine") == engine or e.get("engine_id") == engine]
        return list(rows[-limit:])

    def export(self) -> list[dict[str, Any]]:
        return list(self.events)
