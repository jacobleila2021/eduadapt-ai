"""Teacher workspace UI."""

from __future__ import annotations

import streamlit as st

from engines.learning_experience_platform.service import api_teacher_workspace
from engines.learning_experience_platform.teacher_workspace import (
    teacher_add_teaching_note,
    teacher_assign_activity,
    teacher_lock_section,
    teacher_pin_explanation,
)


def render_teacher_workspace(*, teacher_id: str, lesson_id: str, context: dict | None = None) -> None:
    st.markdown("### Teacher Workspace")
    data = api_teacher_workspace(teacher_id=teacher_id, lesson_id=lesson_id, context=context)
    if not data.get("ok"):
        st.warning(data.get("denied") or "Unavailable")
        return
    st.caption("Track completion · A11y · Revision · Comments")
    for row in data.get("reading_completion") or []:
        st.write(f"{row.get('learner_id')}: {row.get('reading_pct')}%")
    note = st.text_input("Teaching note", key=f"tn_{lesson_id}")
    if st.button("Save teaching note") and note.strip():
        teacher_add_teaching_note(teacher_id, lesson_id, note.strip())
        st.toast("Saved")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Pin explanation"):
            teacher_pin_explanation(teacher_id, lesson_id, "sec_0", "Pinned verified explanation")
    with c2:
        if st.button("Lock section"):
            teacher_lock_section(teacher_id, lesson_id, "sec_0")
    with c3:
        if st.button("Assign checkpoint"):
            teacher_assign_activity(teacher_id, lesson_id, {"type": "checkpoint", "title": "Exit ticket"})
