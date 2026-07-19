"""Scheduler — spaced reviews, reminders, offline sync hooks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
import uuid


class OrchestrationScheduler:
    def __init__(self) -> None:
        self.items: list[dict[str, Any]] = []

    def schedule(
        self,
        *,
        kind: str,
        when_days: int = 1,
        learner_id: str = "",
        session_id: str = "",
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        when = datetime.now(timezone.utc) + timedelta(days=when_days)
        row = {
            "schedule_id": f"sch_{uuid.uuid4().hex[:8]}",
            "kind": kind,  # review|assignment|revision|parent|teacher|intervention|offline_sync
            "due_at": when.isoformat(),
            "day_offset": when_days,
            "learner_id": learner_id,
            "session_id": session_id,
            "payload": payload or {},
            "status": "scheduled",
        }
        self.items.append(row)
        return row

    def from_ale_spaced_repetition(
        self,
        reviews: list[dict[str, Any]],
        *,
        learner_id: str = "",
        session_id: str = "",
    ) -> list[dict[str, Any]]:
        out = []
        for block in reviews or []:
            for s in block.get("sessions") or []:
                out.append(
                    self.schedule(
                        kind="review",
                        when_days=int(s.get("day_offset") or 1),
                        learner_id=learner_id,
                        session_id=session_id,
                        payload={"concept_id": block.get("concept_id"), **s},
                    )
                )
        return out

    def due(self, *, now: datetime | None = None) -> list[dict[str, Any]]:
        now = now or datetime.now(timezone.utc)
        due = []
        for item in self.items:
            try:
                due_at = datetime.fromisoformat(item["due_at"].replace("Z", "+00:00"))
            except Exception:  # noqa: BLE001
                continue
            if due_at <= now and item.get("status") == "scheduled":
                due.append(item)
        return due

    def export(self) -> list[dict[str, Any]]:
        return list(self.items)
