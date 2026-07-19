"""Special educator workspace UI — AIE-grounded."""

from __future__ import annotations

import streamlit as st

from engines.learning_experience_platform.service import api_special_educator_workspace
from engines.learning_experience_platform.special_educator_workspace import sped_add_note


def render_special_educator_workspace(*, educator_id: str, learner_id: str, lesson_id: str = "", context: dict | None = None) -> None:
    st.markdown("### Special Educator Workspace")
    data = api_special_educator_workspace(educator_id=educator_id, learner_id=learner_id, lesson_id=lesson_id, context=context)
    st.json({"accommodations": data.get("accommodation_recommendations"), "ef": data.get("executive_function_supports")})
    kind = st.selectbox("Note type", ["observation", "iep", "therapy", "accommodation", "goal"])
    text = st.text_area("Note", key=f"sped_{lesson_id}")
    if st.button("Save SPED note") and text.strip():
        sped_add_note(educator_id, learner_id, text.strip(), kind=kind, lesson_id=lesson_id)
        st.toast("Saved")
