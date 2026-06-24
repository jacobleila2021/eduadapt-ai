"""
Adaptation pill tabs — reliable on_click navigation + shared styling hooks.
"""

from __future__ import annotations

import streamlit as st

from navigation import PILL_CATEGORIES, spec_by_id
from session_state import VIEW_WORKSPACE, is_workspace, open_adaptation


def _select_category(category_id: str) -> None:
    open_adaptation(category_id)


def _select_spec(spec_id: str) -> None:
    st.session_state.active_output_id = spec_id
    st.session_state.app_view = VIEW_WORKSPACE


def render_pill_navigation(key_prefix: str = "pill") -> None:
    """Cyan pill tabs — opens dedicated workspace via on_click (reliable on Cloud)."""
    active_cat = st.session_state.get("active_category_id", "")
    in_workspace = is_workspace()

    st.markdown(
        '<p class="pill-nav-hint">Tap a version to open its dedicated workspace.</p>',
        unsafe_allow_html=True,
    )

    cols_per_row = 3
    for row_start in range(0, len(PILL_CATEGORIES), cols_per_row):
        row = PILL_CATEGORIES[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, category in zip(cols, row):
            with col:
                is_active = in_workspace and active_cat == category["id"]
                st.button(
                    category["label"],
                    key=f"{key_prefix}_{category['id']}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                    on_click=_select_category,
                    args=(category["id"],),
                )
        for col in cols[len(row) :]:
            with col:
                st.empty()


def render_sub_spec_pills(category_id: str, active_spec_id: str) -> None:
    """Secondary pills inside workspace for multi-version categories."""
    from navigation import category_for_id

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
                on_click=_select_spec,
                args=(spec_id,),
            )
