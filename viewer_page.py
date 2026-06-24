"""
Dedicated adaptation viewer workspace — imported directly by app.py for Cloud reliability.
"""

from __future__ import annotations

import streamlit as st

from docx_exporter import export_tab_docx
from html_exporter import export_tab_html as rich_html_export
from navigation import category_for_id, spec_by_id
from structured_renderers import (
    _coerce_dict,
    content_to_export,
    render_lesson,
    render_vocabulary,
    render_worksheet,
)

from spec_icons import SPEC_ICONS


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
                st.session_state.adaptation_open = True
                st.rerun()
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
                "Print (HTML)",
                data=rich_html_export(title, content, spec_id),
                file_name=html_name,
                mime="text/html",
                use_container_width=True,
                key=f"viewer_html_{spec_id}",
            )
        with c4:
            from audio_learning import (
                OPENAI_VOICE_MAP,
                extract_speech_text,
                generate_openai_speech,
            )

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
    *,
    inline: bool = False,
) -> None:
    """Single adaptation workspace — inline on homepage or standalone."""
    from audio_learning import render_audio_learning_panel

    icon = SPEC_ICONS.get(spec_id, "📘")
    category_id = st.session_state.get("active_category_id", "")

    if inline:
        col_title, col_close = st.columns([5, 1])
        with col_title:
            st.markdown(f"### {icon} {title}")
        with col_close:
            if st.button("Close", key="close_adaptation_panel", use_container_width=True):
                st.session_state.adaptation_open = False
                st.rerun()
    else:
        if st.button("← Back to Workspace", key="back_to_dashboard"):
            st.session_state.adaptation_open = False
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
