"""
Reusable Streamlit UI components: sidebar, analytics cards, downloads.
"""

import streamlit as st

from config import (
    EDUADAPT_TIME_MINUTES,
    MANUAL_TIME_HOURS,
    TIME_SAVED_PERCENT,
)


def render_sidebar() -> None:
    """
    Display time-saved metrics and quick tips in the sidebar.
    """
    st.sidebar.title("EduAdapt AI")
    st.sidebar.caption("Upload Once. Teach Every Learner.")

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
        "**Tip:** Upload a PDF or DOCX lesson plan. "
        "Review analytics, then click **Generate Adaptations**."
    )


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


def render_content_tab(title: str, content: str, download_filename: str) -> None:
    """
    Display markdown content inside a card with a download button.

    Args:
        title: Section title for the download file header.
        content: Markdown or plain text to show.
        download_filename: Filename for the download button.
    """
    with st.container(border=True):
        st.markdown(content)

    full_export = f"# {title}\n\n{content}"
    render_download_button(
        label=f"Download {title}",
        content=full_export,
        filename=download_filename,
    )
