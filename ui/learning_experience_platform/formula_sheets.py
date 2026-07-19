"""Formula sheets UI — verified STEM only."""

from __future__ import annotations

import streamlit as st

from engines.learning_experience_platform.service import api_formula_sheets


def render_formula_sheets(*, subject: str = "", lesson: dict | None = None, context: dict | None = None) -> None:
    st.subheader("Formula Sheets")
    st.caption("Verified STEM engines only — AI cannot invent formulas")
    data = api_formula_sheets(subject=subject, lesson=lesson, context=context)
    for f in data.get("formulae") or []:
        st.markdown(f"**{f.get('name')}**")
        st.code(str(f.get("formula")))
        if f.get("explanation"):
            st.caption(f.get("explanation"))
