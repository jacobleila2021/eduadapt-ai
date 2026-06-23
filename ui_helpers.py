"""
Reusable Streamlit UI components: sidebar, analytics cards, downloads.
"""

from __future__ import annotations

import streamlit as st

from config import (
    EDUADAPT_TIME_MINUTES,
    MANUAL_TIME_HOURS,
    OMNILI_LOGO,
    TIME_SAVED_PERCENT,
)
from content_renderer import render_rich_content
from docx_exporter import export_tab_docx
from html_exporter import export_tab_html
from structured_renderers import (
    content_to_export,
    render_lesson,
    render_vocabulary,
    render_worksheet,
    _coerce_dict,
)

# Navigation icons — defined here so app startup never depends on adaptation_specs exports.
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
    """Time-saved metrics and Omnili branding in the left pane."""
    if OMNILI_LOGO.exists():
        st.sidebar.image(str(OMNILI_LOGO), use_container_width=True)
        st.sidebar.caption("Powered by Omnili")

    st.sidebar.markdown(
        f'<p style="font-size:1.15rem;font-weight:700;color:#22F0FF;margin:0;">EduAdapt AI</p>'
        f'<p style="font-size:0.85rem;opacity:0.9;margin:0.2rem 0 0 0;">Upload Once. Teach Every Learner.</p>',
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("---")
    st.sidebar.subheader("Time Saved")

    st.sidebar.markdown(
        f"""
        <div class="sidebar-metric">
            <small>Estimated Manual Time</small><br>
            <strong>{MANUAL_TIME_HOURS} Hours</strong>
        </div>
        <div class="sidebar-metric">
            <small>EduAdapt Time</small><br>
            <strong>{EDUADAPT_TIME_MINUTES} Minutes</strong>
        </div>
        <div class="sidebar-metric">
            <small>Time Saved</small><br>
            <strong>{TIME_SAVED_PERCENT}%</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Tip:** All adaptation versions stay on one page below — open any section without reloading."
    )


def render_adaptation_section(
    spec: dict,
    content: str | dict,
    base_name: str,
    expanded: bool = False,
) -> None:
    """One adaptation block inside an expander — others on the page stay open."""
    icon = SPEC_ICONS.get(spec["id"], "📘")
    filename = f"{base_name}_{spec['id']}.txt"
    label = f"{icon}  {spec['tab']}"
    with st.expander(label, expanded=expanded):
        st.markdown(f"**{spec['title']}**")
        render_content_tab(spec["title"], content, filename, spec_id=spec["id"])


def render_analytics_panel(analytics: dict) -> None:
    """
    Show lesson complexity, reading level, and objective count in cards.

    Args:
        analytics: Output from analytics_engine.build_analytics_report.
    """
    st.subheader("Lesson Analytics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>Lesson Complexity Score</h4>
                <p>{analytics['complexity_score']}/100</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>Estimated Reading Level</h4>
                <p>{analytics['reading_level']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <h4>Learning Objectives</h4>
                <p>{analytics['objective_count']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_download_button(label: str, content: str, filename: str) -> None:
    """
    Add a download button for a single output tab.

    Args:
        label: Button text shown to the teacher.
        content: Text file content to download.
        filename: Suggested filename (e.g. dyslexia_lesson.txt).
    """
    st.download_button(
        label=label,
        data=content,
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
    )


def render_adaptation_nav(specs: list, active_id: str, columns: int = 4) -> None:
    """Deprecated — use render_adaptation_section on one page instead."""
    for spec in specs:
        st.caption(f"• {spec['tab']}")


def render_content_tab(
    title: str,
    content: str | dict,
    download_filename: str,
    spec_id: str = "",
) -> None:
    """
    Display content inside a card with a download button.
    Routes vocabulary, worksheet, and structured lessons to native renderers.
    """
    with st.container(border=True):
        if spec_id == "vocabulary":
            render_vocabulary(content)
        elif spec_id == "worksheet":
            render_worksheet(content, key_prefix=spec_id)
        elif _coerce_dict(content):
            render_lesson(_coerce_dict(content))
        else:
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
