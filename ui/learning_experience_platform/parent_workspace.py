"""Parent workspace UI — curriculum locked."""

from __future__ import annotations

import streamlit as st

from engines.learning_experience_platform.parent_workspace import parent_encouragement, parent_home_note, parent_mark_practice
from engines.learning_experience_platform.service import api_parent_workspace


def render_parent_workspace(*, parent_id: str, learner_id: str, lesson_id: str, context: dict | None = None) -> None:
    st.markdown("### Parent Workspace")
    st.info("Parents can view progress and leave encouragement — curriculum cannot be altered.")
    data = api_parent_workspace(parent_id=parent_id, learner_id=learner_id, lesson_id=lesson_id, context=context)
    prog = data.get("progress") or {}
    st.metric("Reading %", f"{float(prog.get('reading_pct') or 0):.0f}")
    msg = st.text_input("Encouragement", key=f"pe_{lesson_id}")
    if st.button("Send encouragement") and msg.strip():
        parent_encouragement(parent_id, lesson_id, msg.strip(), learner_id=learner_id)
        st.toast("Sent")
    note = st.text_input("Home-learning note", key=f"ph_{lesson_id}")
    if st.button("Save home note") and note.strip():
        parent_home_note(parent_id, lesson_id, note.strip())
    if st.button("Mark practice complete"):
        parent_mark_practice(parent_id, lesson_id)
        st.toast("Marked")
