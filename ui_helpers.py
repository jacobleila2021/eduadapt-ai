"""
Reusable Streamlit UI components for Alora AI.
"""

from __future__ import annotations

import streamlit as st

from config import APP_NAME, APP_TAGLINE

from structured_renderers import (
    content_to_export,
    render_lesson,
    render_vocabulary,
    render_worksheet,
    _coerce_dict,
)
from docx_exporter import export_tab_docx
from html_exporter import export_tab_html

SPEC_ICONS = {
    "original": "📄",
    "vocabulary": "📚",
    "standard": "✨",
    "ld": "♿",
    "dyslexia": "🔤",
    "dysgraphia": "✍️",
    "dyscalculia": "🔢",
    "adhd": "⚡",
    "autism": "🧩",
    "executive": "📋",
    "visual": "👁️",
    "auditory": "👂",
    "ell": "🌍",
    "gifted": "🚀",
    "parent": "🏠",
    "teacher": "👩‍🏫",
    "tutor": "🤖",
    "multisensory": "🎨",
    "worksheet": "📝",
}


def render_sidebar() -> None:
    """Two coloured tips only — clean left pane."""
    st.sidebar.markdown(
        """
        <div class="sidebar-tip">
            <span class="sidebar-tip-num">1</span>
            <strong>Study order:</strong> Open <strong>Vocabulary</strong> first,
            then learner versions, then the <strong>Worksheet</strong>.
        </div>
        <div class="sidebar-tip">
            <span class="sidebar-tip-num">2</span>
            <strong>Switch freely:</strong> Pick any version below — your adaptations
            stay loaded; you never need to regenerate.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_brand_header(logo_path: str | None = None) -> None:
    """Logo top-left + Alora AI title (single image on page)."""
    col_logo, col_text = st.columns([1, 5], vertical_alignment="center")
    with col_logo:
        if logo_path:
            st.image(logo_path, width=110)
    with col_text:
        st.markdown(
            f"""
            <div class="alora-header" style="border:none;box-shadow:none;padding:0;">
                <p class="alora-title">{APP_NAME}</p>
                <p class="alora-tagline">{APP_TAGLINE}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_adaptation_nav(specs: list, active_id: str, columns: int = 4) -> None:
    """Tab grid — labels always visible; selection stored in session (no reload)."""
    st.markdown(
        '<p class="adapt-nav-hint"><strong>All versions stay loaded.</strong> '
        "Click a label to view that lesson — nothing closes or regenerates.</p>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="adapt-nav-grid">', unsafe_allow_html=True)
    for row_start in range(0, len(specs), columns):
        row_specs = specs[row_start : row_start + columns]
        cols = st.columns(columns)
        for col, spec in zip(cols, row_specs):
            icon = SPEC_ICONS.get(spec["id"], "📘")
            label = f"{icon} {spec['tab']}"
            with col:
                is_active = spec["id"] == active_id
                if st.button(
                    label,
                    key=f"adapt_nav_{spec['id']}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    if spec["id"] != active_id:
                        st.session_state.active_output_id = spec["id"]
        for col in cols[len(row_specs) :]:
            with col:
                st.empty()
    st.markdown("</div>", unsafe_allow_html=True)


def render_analytics_panel(analytics: dict) -> None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>Complexity Score</h4>
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
                <h4>Objectives Found</h4>
                <p>{analytics['objective_count']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_content_tab(
    title: str,
    content: str | dict,
    download_filename: str,
    spec_id: str = "",
) -> None:
    """Structured lesson / vocabulary / worksheet — original formatting."""
    with st.container(border=True):
        if spec_id == "vocabulary":
            render_vocabulary(content)
        elif spec_id == "worksheet":
            render_worksheet(content, key_prefix=spec_id)
        elif _coerce_dict(content):
            render_lesson(_coerce_dict(content))
        else:
            from content_renderer import render_rich_content
            render_rich_content(str(content))

    full_export = content_to_export(title, content, spec_id)
    col_txt, col_docx, col_html = st.columns(3)
    with col_txt:
        st.download_button(
            label="Text",
            data=full_export,
            file_name=download_filename,
            mime="text/plain",
            use_container_width=True,
            key=f"dl_txt_{spec_id}",
        )
    with col_docx:
        docx_name = download_filename.rsplit(".", 1)[0] + ".docx"
        st.download_button(
            label="Word (LD friendly)",
            data=export_tab_docx(title, content, spec_id),
            file_name=docx_name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key=f"dl_docx_{spec_id}",
        )
    with col_html:
        html_name = download_filename.rsplit(".", 1)[0] + ".html"
        st.download_button(
            label="HTML (print / colour)",
            data=export_tab_html(title, content, spec_id),
            file_name=html_name,
            mime="text/html",
            use_container_width=True,
            key=f"dl_html_{spec_id}",
        )
