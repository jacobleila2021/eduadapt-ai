"""Motivation notifications — AIE-aware, non-manipulative."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def notify(
    *,
    learner_id: str,
    kind: str,
    title: str,
    body: str,
    personalization: dict[str, Any] | None = None,
) -> dict[str, Any]:
    personalization = personalization or {}
    if personalization.get("notification_style") == "gentle":
        title = title.replace("!", "")
        body = body.replace("!", ".")
    return {
        "notification_id": f"ntf_{uuid.uuid4().hex[:8]}",
        "learner_id": learner_id,
        "kind": kind,  # xp|badge|quest|certificate|streak
        "title": title,
        "body": body,
        "ts": _now(),
        "dark_pattern": False,
        "urgency_pressure": False,
    }
