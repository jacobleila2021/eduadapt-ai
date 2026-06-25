"""
Reusable Streamlit UI components for Alora AI — premium layout.
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from config import APP_NAME, APP_TAGLINE


def _logo_data_uri(logo_path: str | None) -> str | None:
    if not logo_path or not Path(logo_path).exists():
        return None
    raw = Path(logo_path).read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/png;base64,{b64}"


def render_top_nav(logo_path: str | None = None, version: str = "") -> None:
    """Fixed brand signage bar — logo left, Alora AI centred, platform address right."""
    data_uri = _logo_data_uri(logo_path)
    logo_html = (
        f'<img src="{data_uri}" alt="Alora AI logo" class="topnav-logo-img"/>'
        if data_uri
        else ""
    )
    version_html = f'<span class="topnav-version">v{version}</span>' if version else ""
    st.markdown(
        f"""
        <div class="alora-topnav">
          <div class="topnav-accent"></div>
          <div class="topnav-inner">
            <div class="topnav-logo">{logo_html}</div>
            <div class="topnav-center">
              <div class="topnav-title">
                <span class="name-alora">Alora</span><span class="name-ai"> AI</span>
              </div>
              <div class="topnav-tagline">{APP_TAGLINE}</div>
            </div>
            <div class="topnav-right">
              <span class="topnav-address">Adaptive Learning Platform</span>
              <span class="topnav-url">eduadapt-ai.streamlit.app</span>
              {version_html}
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(version: str) -> None:
    """Premium sidebar — multimodal, adaptive, AI blocks."""
    st.sidebar.markdown(
        """
        <div class="sidebar-block">
          <p class="sidebar-block-title">◆ Multimodal Learning</p>
          <div class="sidebar-item">Reading</div>
          <div class="sidebar-item">Listening</div>
          <div class="sidebar-item">Visual Learning</div>
          <div class="sidebar-item">Interactive Learning</div>
        </div>
        <hr class="sidebar-divider"/>
        <div class="sidebar-block">
          <p class="sidebar-block-title">◆ Adaptive Learning</p>
          <div class="sidebar-item">Personalised pathways</div>
          <div class="sidebar-item">Inclusive learning</div>
          <div class="sidebar-item">Accessibility first</div>
        </div>
        <hr class="sidebar-divider"/>
        <div class="sidebar-block">
          <p class="sidebar-block-title">◆ AI Powered</p>
          <div class="sidebar-item">Intelligent lesson adaptation</div>
          <div class="sidebar-item">Teacher support</div>
          <div class="sidebar-item">Student success</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f"""
        <p class="sidebar-meta">Version: {version}</p>
        <div class="sidebar-creator">
          <span class="sidebar-creator-label">Creator</span>
          <span class="sidebar-creator-name">Leila Jacob</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard_intro() -> None:
    """Homepage hero — workspace, not lesson output."""
    st.markdown(
        f"""
        <div class="dashboard-hero">
          <h2>{APP_NAME} Workspace</h2>
          <p>{APP_TAGLINE}</p>
          <div class="multimodal-strip">
            <span class="multimodal-chip">📖 Reading</span>
            <span class="multimodal-chip">🎧 Listening</span>
            <span class="multimodal-chip">👁 Visual</span>
            <span class="multimodal-chip">✨ Interactive</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pill_navigation() -> None:
    """Dashboard adaptation pills."""
    from pill_tabs import render_pill_navigation as _render_pills

    _render_pills(key_prefix="pill")


def render_analytics_panel(analytics: dict) -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>Lesson Complexity</h4>
                <p>{analytics['complexity_score']}/100</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>Reading Level</h4>
                <p>{analytics['reading_level']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>Objectives</h4>
                <p>{analytics['objective_count']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# Legacy alias for imports
def render_brand_header(logo_path: str | None = None) -> None:
    render_top_nav(logo_path)


def render_adaptation_nav(specs: list, active_id: str, columns: int = 4) -> None:
    """Legacy grid — redirects to pill style."""
    render_pill_navigation()


def render_content_tab(
    title: str,
    content: str | dict,
    download_filename: str,
    spec_id: str = "",
) -> None:
    """Legacy inline tab — delegates to viewer_page."""
    from viewer_page import render_adaptation_viewer

    render_adaptation_viewer(
        spec_id,
        title,
        content,
        download_filename,
        zip_bytes=None,
        base_name=download_filename.rsplit("_", 1)[0],
        api_key=st.session_state.get("runtime_api_key", ""),
    )
