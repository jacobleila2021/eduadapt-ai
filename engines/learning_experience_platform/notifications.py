"""Notifications facade for LXP Phase 3."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.collab_store import load_notifications, push_notification


def api_list_notifications(user_id: str) -> dict[str, Any]:
    return {"ok": True, "notifications": load_notifications(user_id)}


def api_notify(user_id: str, *, type: str, **payload: Any) -> dict[str, Any]:
    return {"ok": True, "notification": push_notification(user_id, {"type": type, **payload})}
