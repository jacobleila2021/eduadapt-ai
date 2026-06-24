"""
Single source of truth for Alora AI navigation and adaptation selection.
Session state only — query params are NOT written (they can reset Cloud sessions).
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


def close_workspace() -> None:
    st.session_state.app_view = VIEW_DASHBOARD


def clear_stale_url_params() -> None:
    """Remove orphaned ?view=workspace from URL when session has no adaptations."""
    try:
        if st.query_params.get("view") == "workspace" and not st.session_state.get("adaptations"):
            st.query_params.clear()
    except Exception:
        pass


def is_workspace() -> bool:
    return st.session_state.get("app_view") == VIEW_WORKSPACE


def should_render_workspace() -> bool:
    return bool(st.session_state.get("adaptations")) and is_workspace()
