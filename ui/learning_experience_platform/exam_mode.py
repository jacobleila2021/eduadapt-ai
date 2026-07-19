"""Exam mode UI — AME official items."""

from __future__ import annotations

import streamlit as st

from engines.learning_experience_platform.service import api_exam_mode, api_official_exam


def render_exam_mode(*, learner_id: str, topic: str = "", lesson_text: str = "", context: dict | None = None) -> None:
    st.subheader("Official Exam Mode")
    mode = st.selectbox("Mode", ["practice", "timed", "review", "teacher"])
    data = api_exam_mode(learner_id=learner_id, topic=topic, lesson_text=lesson_text, mode=mode, context=context)
    st.caption("Companion suppressed during assessment")
    for q in data.get("questions") or []:
        st.markdown(f"**[{q.get('bloom')}] ({q.get('marks')}m)** {q.get('question')}")
        if q.get("answer_revealed") and q.get("official_answer"):
            st.success(f"Official: {q.get('official_answer')}")
    if mode == "teacher":
        with st.expander("Official exam bundle"):
            st.json(api_official_exam(topic=topic, learner_id=learner_id).get("categories"))
