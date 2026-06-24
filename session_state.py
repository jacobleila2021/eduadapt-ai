"""
Single source of truth for Alora AI navigation and adaptation selection.
"""

from __future__ import annotations

import streamlit as st

from navigation import default_spec_for_category

VIEW_DASHBOARD = "dashboard"
VIEW_WORKSPACE = "workspace"


def init_navigation_state() -> None:
    defaults = {
        "app_view": VIEW_DASHBOARD,
        "active_category_id": "vocabulary",
        "active_output_id": "vocabulary",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def open_adaptation(category_id: str, spec_id: str | None = None) -> None:
    """Open exactly one adaptation in the dedicated workspace."""
    st.session_state.active_category_id = category_id
    st.session_state.active_output_id = spec_id or default_spec_for_category(category_id)
    st.session_state.app_view = VIEW_WORKSPACE
    # Query params backup — survives odd Cloud rerun behaviour
    try:
        st.query_params["view"] = "workspace"
        st.query_params["cat"] = category_id
        st.query_params["spec"] = st.session_state.active_output_id
    except Exception:
        pass


def close_workspace() -> None:
    st.session_state.app_view = VIEW_DASHBOARD
    try:
        st.query_params.clear()
    except Exception:
        pass


def sync_from_query_params() -> None:
    """Restore workspace route from URL if session was reset."""
    try:
        if st.query_params.get("view") == "workspace" and st.session_state.get("adaptations"):
            st.session_state.app_view = VIEW_WORKSPACE
            if cat := st.query_params.get("cat"):
                st.session_state.active_category_id = cat
            if spec := st.query_params.get("spec"):
                st.session_state.active_output_id = spec
    except Exception:
        pass


def is_workspace() -> bool:
    return st.session_state.get("app_view") == VIEW_WORKSPACE
