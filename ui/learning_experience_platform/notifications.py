"""Notifications UI."""

from __future__ import annotations

import streamlit as st

from engines.learning_experience_platform.service import api_notifications


def render_notifications(user_id: str) -> None:
    st.subheader("Notifications")
    for n in api_notifications(user_id).get("notifications") or []:
        st.caption(f"{n.get('type')}: {n.get('lesson_id') or ''} · {n.get('created_at')}")
