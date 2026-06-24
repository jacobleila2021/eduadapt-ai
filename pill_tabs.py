"""
Adaptation pill tabs — opens dedicated workspace on click.
Uses on_click callbacks so navigation runs BEFORE dashboard file-upload logic.
"""

from __future__ import annotations

import streamlit as st

from navigation import PILL_CATEGORIES, category_for_id, category_for_spec, spec_by_id
from session_state import VIEW_WORKSPACE, is_workspace, open_adaptation


def _make_category_handler(category_id: str):
    def _handler() -> None:
        open_adaptation(category_id)

    return _handler


def _make_spec_handler(spec_id: str):
    def _handler() -> None:
        st.session_state.active_output_id = spec_id
        cat = category_for_spec(spec_id)
        if cat:
            st.session_state.active_category_id = cat["id"]
        st.session_state.app_view = VIEW_WORKSPACE
        try:
            st.query_params["view"] = "workspace"
            st.query_params["spec"] = spec_id
            if cat:
                st.query_params["cat"] = cat["id"]
        except Exception:
            pass

    return _handler


def render_pill_navigation(key_prefix: str = "pill") -> None:
    """Dark cyan pills — one click opens the dedicated workspace."""
    active_cat = st.session_state.get("active_category_id", "")
    in_workspace = is_workspace()

    st.markdown(
        '<p class="pill-nav-hint">Click a version — it opens in a dedicated workspace.</p>',
        unsafe_allow_html=True,
    )

    cols_per_row = 3
    for row_start in range(0, len(PILL_CATEGORIES), cols_per_row):
        row = PILL_CATEGORIES[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, category in zip(cols, row):
            with col:
                cat_id = category["id"]
                is_active = in_workspace and active_cat == cat_id
                st.button(
                    category["label"],
                    key=f"{key_prefix}_{cat_id}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                    on_click=_make_category_handler(cat_id),
                )
        for col in cols[len(row) :]:
            with col:
                st.empty()


def render_sub_spec_pills(category_id: str, active_spec_id: str) -> None:
    """Secondary pills for categories with multiple versions."""
    category = category_for_id(category_id)
    if not category or len(category["spec_ids"]) <= 1:
        return

    st.markdown("**Versions in this category**")
    spec_ids = category["spec_ids"]
    cols = st.columns(min(len(spec_ids), 5))
    for col, spec_id in zip(cols, spec_ids):
        spec = spec_by_id(spec_id)
        if not spec:
            continue
        with col:
            st.button(
                spec["tab"],
                key=f"subpill_{spec_id}",
                use_container_width=True,
                type="primary" if spec_id == active_spec_id else "secondary",
                on_click=_make_spec_handler(spec_id),
            )
