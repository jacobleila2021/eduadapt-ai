"""Notification coordination — students, teachers, parents, admins."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class NotificationManager:
    AUDIENCES = ("student", "teacher", "parent", "school_admin", "district_admin")

    def __init__(self) -> None:
        self.outbox: list[dict[str, Any]] = []
        self.preferences: dict[str, dict[str, bool]] = {}

    def set_preferences(self, user_id: str, prefs: dict[str, bool]) -> None:
        self.preferences[user_id] = prefs

    def notify(
        self,
        *,
        audience: str,
        user_id: str,
        title: str,
        body: str,
        channel: str = "in_app",
        meta: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        prefs = self.preferences.get(user_id) or {}
        if prefs.get(channel) is False or prefs.get(audience) is False:
            return None
        row = {
            "notification_id": f"ntf_{uuid.uuid4().hex[:8]}",
            "audience": audience,
            "user_id": user_id,
            "title": title,
            "body": body,
            "channel": channel,
            "meta": meta or {},
            "ts": _now(),
            "status": "queued",
        }
        self.outbox.append(row)
        return row

    def from_decisions(
        self,
        decisions: list[dict[str, Any]],
        *,
        learner_id: str,
        teacher_id: str = "",
        parent_id: str = "",
    ) -> list[dict[str, Any]]:
        sent = []
        for d in decisions:
            if d.get("decision_type") == "engagement" and learner_id:
                n = self.notify(
                    audience="student",
                    user_id=learner_id,
                    title="Keep going",
                    body="A short activity is ready when you are.",
                    meta={"decision_id": d.get("decision_id")},
                )
                if n:
                    sent.append(n)
            if d.get("decision_type") == "misconception_intervention" and teacher_id:
                n = self.notify(
                    audience="teacher",
                    user_id=teacher_id,
                    title="Misconception detected",
                    body=d.get("reason") or "",
                    meta={"decision_id": d.get("decision_id")},
                )
                if n:
                    sent.append(n)
            if d.get("decision_type") == "remediation" and parent_id:
                n = self.notify(
                    audience="parent",
                    user_id=parent_id,
                    title="Study tip",
                    body="A short review plan was suggested for your learner.",
                    meta={"decision_id": d.get("decision_id")},
                )
                if n:
                    sent.append(n)
        return sent

    def export(self) -> list[dict[str, Any]]:
        return list(self.outbox)
