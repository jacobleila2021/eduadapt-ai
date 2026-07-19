"""Role dashboards UI."""

from __future__ import annotations

import streamlit as st

from engines.learning_experience_platform.service import api_workspace_dashboard


def render_role_dashboard(*, role: str, user_id: str, learner_id: str = "", lesson_id: str = "", context: dict | None = None) -> None:
    data = api_workspace_dashboard(
        role=role,
        user_id=user_id,
        learner_id=learner_id,
        lesson_id=lesson_id,
        context=context,
    )
    st.caption(f"Workspace: {data.get('workspace') or role}")
    if data.get("policy"):
        st.caption(str(data["policy"]))
