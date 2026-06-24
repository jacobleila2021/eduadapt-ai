"""
Reusable Streamlit UI components for Alora AI — premium layout.
"""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from config import APP_NAME, APP_TAGLINE
from navigation import PILL_CATEGORIES, category_for_id, spec_by_id

from structured_renderers import (
    content_to_export,
    render_lesson,
    render_vocabulary,
    render_worksheet,
    _coerce_dict,
)
from docx_exporter import export_tab_docx, export_tab_html
from html_exporter import export_tab_html as rich_html_export
from audio_learning import render_audio_learning_panel

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


def _logo_data_uri(logo_path: str | None) -> str | None:
    if not logo_path or not Path(logo_path).exists():
        return None
    raw = Path(logo_path).read_bytes()
    b64 = base64.b64encode(raw).decode("ascii")
    return f"data:image/png;base64,{b64}"


def render_top_nav(logo_path: str | None = None) -> None:
    """Fixed brand signage bar — logo left, Alora AI centred, platform address right."""
    data_uri = _logo_data_uri(logo_path)
    logo_html = (
        f'<img src="{data_uri}" alt="Alora AI logo" class="topnav-logo-img"/>'
        if data_uri
        else ""
    )
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
          <div class="sidebar-item">Personalized pathways</div>
          <div class="sidebar-item">Inclusive content delivery</div>
          <div class="sidebar-item">Accessibility-first design</div>
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
        <p class="sidebar-meta">
          Version: {version}<br/>
          Creator: Leila Jacob
        </p>
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


def render_pill_navigation(active_category_id: str | None = None) -> str | None:
    """
    Rounded pill tabs — clicking opens dedicated viewer (returns selected spec_id).
    """
    st.markdown(
        '<p class="pill-nav-hint">Select an adaptation to open in its dedicated workspace.</p>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="pill-nav-grid">', unsafe_allow_html=True)

    selected_spec: str | None = None
    cols_per_row = 3
    for row_start in range(0, len(PILL_CATEGORIES), cols_per_row):
        row = PILL_CATEGORIES[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, category in zip(cols, row):
            with col:
                is_active = category["id"] == active_category_id
                if st.button(
                    category["label"],
                    key=f"pill_{category['id']}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                ):
                    selected_spec = category["spec_ids"][0]
                    st.session_state.active_category_id = category["id"]
                    st.session_state.active_output_id = selected_spec
                    st.session_state.app_view = "viewer"
        for col in cols[len(row) :]:
            with col:
                st.empty()

    st.markdown("</div>", unsafe_allow_html=True)
    return selected_spec


def render_sub_spec_pills(category_id: str, active_spec_id: str) -> None:
    """Secondary pills when a category has multiple adaptations."""
    category = category_for_id(category_id)
    if not category or len(category["spec_ids"]) <= 1:
        return

    st.markdown("**Versions in this category**")
    st.markdown('<div class="sub-pill-row pill-nav-grid">', unsafe_allow_html=True)
    spec_ids = category["spec_ids"]
    cols = st.columns(min(len(spec_ids), 5))
    for col, spec_id in zip(cols, spec_ids):
        spec = spec_by_id(spec_id)
        if not spec:
            continue
        label = spec["tab"]
        with col:
            if st.button(
                label,
                key=f"subpill_{spec_id}",
                use_container_width=True,
                type="primary" if spec_id == active_spec_id else "secondary",
            ):
                st.session_state.active_output_id = spec_id
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_analytics_panel(analytics: dict) -> None:
    st.markdown('<div class="workspace-card">', unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)


def render_viewer_downloads(
    title: str,
    content: str | dict,
    spec_id: str,
    download_filename: str,
    zip_bytes: bytes | None,
    base_name: str,
) -> None:
    """Download This Version + Download All Adaptations."""
    st.markdown("---")
    st.markdown("#### Downloads")
    col_one, col_all = st.columns(2)

    with col_one:
        st.caption("Option 1 — This version")
        c1, c2, c3, c4 = st.columns(4)
        full_export = content_to_export(title, content, spec_id)
        with c1:
            st.download_button(
                "Text",
                data=full_export,
                file_name=download_filename,
                mime="text/plain",
                use_container_width=True,
                key=f"viewer_txt_{spec_id}",
            )
        with c2:
            docx_name = download_filename.rsplit(".", 1)[0] + ".docx"
            st.download_button(
                "Word",
                data=export_tab_docx(title, content, spec_id),
                file_name=docx_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key=f"viewer_docx_{spec_id}",
            )
        with c3:
            html_name = download_filename.rsplit(".", 1)[0] + ".html"
            st.download_button(
                "HTML",
                data=rich_html_export(title, content, spec_id),
                file_name=html_name,
                mime="text/html",
                use_container_width=True,
                key=f"viewer_html_{spec_id}",
            )
        with c4:
            from audio_learning import extract_speech_text, generate_openai_speech, OPENAI_VOICE_MAP

            api_key = st.session_state.get("runtime_api_key", "")
            voice = st.session_state.get("audio_voice", "Female Professional")
            speech = extract_speech_text(title, content, spec_id)
            mp3 = generate_openai_speech(
                speech, OPENAI_VOICE_MAP.get(voice, "nova"), api_key
            )
            if mp3:
                st.download_button(
                    "MP3",
                    data=mp3,
                    file_name=f"{base_name}_{spec_id}.mp3",
                    mime="audio/mpeg",
                    use_container_width=True,
                    key=f"viewer_mp3_{spec_id}",
                )

    with col_all:
        st.caption("Option 2 — All adaptations")
        if zip_bytes:
            st.download_button(
                "Download All (ZIP — HTML + Word per version)",
                data=zip_bytes,
                file_name=f"{base_name}_alora_print_pack.zip",
                mime="application/zip",
                use_container_width=True,
                key="viewer_zip_all",
            )
        bundle = st.session_state.get("_text_bundle_cache")
        if bundle:
            st.download_button(
                "Download All (Plain text bundle)",
                data=bundle,
                file_name=f"{base_name}_alora_bundle.txt",
                mime="text/plain",
                use_container_width=True,
                key="viewer_txt_all",
            )


def render_adaptation_viewer(
    spec_id: str,
    title: str,
    content: str | dict,
    download_filename: str,
    zip_bytes: bytes | None,
    base_name: str,
    api_key: str,
) -> None:
    """Dedicated workspace — single adaptation only."""
    icon = SPEC_ICONS.get(spec_id, "📘")
    category_id = st.session_state.get("active_category_id", "")

    if st.button("← Back to Workspace", key="back_to_dashboard"):
        st.session_state.app_view = "dashboard"
        st.rerun()

    st.markdown(
        f"""
        <div class="viewer-header">
          <h2>{icon} {title}</h2>
          <p>Dedicated viewing workspace — typography, layout, and accessibility preserved for print & export.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_sub_spec_pills(category_id, spec_id)

    auditory_mode = st.toggle(
        "Auditory Learning Mode",
        value=st.session_state.get("auditory_mode", False),
        help="Larger audio controls and listening-focused layout.",
        key=f"auditory_toggle_{spec_id}",
    )
    st.session_state.auditory_mode = auditory_mode

    if auditory_mode:
        st.markdown(
            "<style>.main .block-container { max-width: 900px !important; }</style>",
            unsafe_allow_html=True,
        )

    render_audio_learning_panel(
        title, content, spec_id, api_key, auditory_mode=auditory_mode
    )

    st.markdown("---")
    st.markdown("#### Lesson Content")

    with st.container(border=True):
        if spec_id == "vocabulary":
            render_vocabulary(content)
        elif spec_id == "worksheet":
            render_worksheet(content, key_prefix=f"viewer_{spec_id}")
        elif _coerce_dict(content):
            render_lesson(_coerce_dict(content))
        else:
            from content_renderer import render_rich_content

            render_rich_content(str(content))

    render_viewer_downloads(
        title, content, spec_id, download_filename, zip_bytes, base_name
    )


# Legacy alias for imports
def render_brand_header(logo_path: str | None = None) -> None:
    render_top_nav(logo_path)


def render_adaptation_nav(specs: list, active_id: str, columns: int = 4) -> None:
    """Legacy grid — redirects to pill style."""
    render_pill_navigation(st.session_state.get("active_category_id"))


def render_content_tab(
    title: str,
    content: str | dict,
    download_filename: str,
    spec_id: str = "",
) -> None:
    """Legacy inline tab — used only if viewer not active."""
    render_adaptation_viewer(
        spec_id,
        title,
        content,
        download_filename,
        zip_bytes=None,
        base_name=download_filename.rsplit("_", 1)[0],
        api_key=st.session_state.get("runtime_api_key", ""),
    )
