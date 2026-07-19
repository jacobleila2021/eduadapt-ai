"""Revision planner UI."""

from __future__ import annotations

import streamlit as st

from engines.learning_experience_platform.service import api_revision_planner


def render_revision_planner(*, learner_id: str, topic: str = "", context: dict | None = None) -> None:
    st.subheader("Revision Planner")
    days = st.slider("Days until exam", 1, 60, 14)
    mins = st.slider("Minutes / day", 15, 120, 45)
    data = api_revision_planner(
        learner_id=learner_id,
        exam_days=days,
        available_minutes_per_day=mins,
        topic=topic,
        context=context,
    )
    for day in (data.get("schedule") or [])[:7]:
        st.write(f"Day +{day.get('day_offset')}: {day.get('focus')} · {day.get('minutes')} min · {', '.join(day.get('activities') or [])}")
