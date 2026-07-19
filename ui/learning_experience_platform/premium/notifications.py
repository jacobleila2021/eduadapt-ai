"""Unified notification center UI."""

from __future__ import annotations

from typing import Any

import streamlit as st

from engines.learning_experience_platform.phase4_settings import notification_preferences
from engines.learning_experience_platform.service import api_notifications


def render_notification_center(user_id: str) -> dict[str, Any]:
    st.subheader("Notifications")
    prefs = notification_preferences(user_id)
    st.caption("Customize channels in Settings")
    rows = api_notifications(user_id).get("notifications") or []
    # Synthetic category labels for empty states
    categories = [
        "lesson_reminders",
        "revision_reminders",
        "teacher_comments",
        "parent_messages",
        "companion_updates",
        "achievement_unlocks",
        "offline_sync_status",
        "system_announcements",
    ]
    if not rows:
        st.write("No notifications yet.")
        st.caption("Channels: " + ", ".join(categories))
    for n in rows[:30]:
        st.markdown(
            f'<div class="lxp-notify lxp-premium">{n.get("type")}: '
            f'{n.get("lesson_id") or ""} · {n.get("created_at") or ""}</div>',
            unsafe_allow_html=True,
        )
    return {"ok": True, "count": len(rows), "prefs": prefs}
