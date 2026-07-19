"""Revision mode UI."""

from __future__ import annotations

import streamlit as st

from engines.learning_experience_platform.service import api_revision_mode


def render_revision_mode(*, learner_id: str, lesson: dict | None = None, context: dict | None = None) -> None:
    st.subheader("Revision Mode")
    data = api_revision_mode(learner_id=learner_id, lesson=lesson, context=context)
    st.caption("Distraction-free · verified sources only")
    for idea in (data.get("chapter_summaries") or [])[:6]:
        st.write(f"• {str(idea)[:200]}")
    if data.get("common_misconceptions"):
        with st.expander("Common misconceptions"):
            st.write(data["common_misconceptions"][:5])
    presets = data.get("a11y_revision_presets") or {}
    st.selectbox("A11y revision preset", list(presets.keys()) or ["default"])
