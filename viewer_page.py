"""
Dedicated adaptation viewer workspace — imported directly by app.py for Cloud reliability.
"""

from __future__ import annotations

import streamlit as st

from accessibility import render_accessibility_toolbar
from docx_exporter import export_tab_docx
from html_exporter import export_tab_html as rich_html_export
from structured_renderers import (
    _coerce_dict,
    content_to_export,
    render_lesson,
    render_vocabulary,
    render_worksheet,
)

from spec_icons import SPEC_ICONS
from publication_gate import publication_block_reason


def render_viewer_downloads(
    title: str,
    content: str | dict,
    spec_id: str,
    download_filename: str,
    zip_bytes: bytes | None,
    base_name: str,
) -> None:
    """Download This Version + Download All Adaptations."""
    block_reason = publication_block_reason(
        st.session_state.get("adaptations"),
        package=st.session_state.get("vlie_package"),
        quality=st.session_state.get("quality"),
    )
    if block_reason:
        st.error(f"Downloads are disabled because publication QA failed: {block_reason}")
        return
    st.markdown("---")
    st.markdown("#### Downloads")
    col_one, col_all = st.columns(2)

    with col_one:
        st.caption("Option 1 — This version")
        try:
            full_export = content_to_export(title, content, spec_id)
            docx_export = export_tab_docx(title, content, spec_id)
            html_export = rich_html_export(title, content, spec_id)
        except Exception:
            st.error(
                "**Export** — This adaptation could not be packaged safely."
            )
            st.info("Recovery: reopen the adaptation and retry the export.")
            return
        c1, c2, c3, c4 = st.columns(4)
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
                data=docx_export,
                file_name=docx_name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key=f"viewer_docx_{spec_id}",
            )
        with c3:
            html_name = download_filename.rsplit(".", 1)[0] + ".html"
            st.download_button(
                "Print (HTML)",
                data=html_export,
                file_name=html_name,
                mime="text/html",
                use_container_width=True,
                key=f"viewer_html_{spec_id}",
            )
        with c4:
            from audio_learning import (
                VOICE_OPTIONS,
                extract_speech_text,
                generate_openai_speech_result,
            )

            api_key = st.session_state.get("runtime_api_key", "")
            voice = st.session_state.get("audio_voice", "Female")
            meta = VOICE_OPTIONS.get(voice) or next(iter(VOICE_OPTIONS.values()))
            speech = extract_speech_text(title, content, spec_id)
            audio_result = generate_openai_speech_result(
                speech, meta["openai"], api_key, meta.get("instructions", "")
            )
            mp3 = audio_result.get("payload") if audio_result.get("ok") else None
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
    hide_downloads: bool = False,
    lesson_title: str = "",
) -> None:
    """Single adaptation content panel — audio top, lesson body, tabs at page bottom."""
    block_reason = publication_block_reason(
        st.session_state.get("adaptations"),
        package=st.session_state.get("vlie_package"),
        quality=st.session_state.get("quality"),
    )
    if block_reason:
        st.error(
            "This lesson is quarantined and cannot be viewed, narrated, or exported: "
            f"{block_reason}"
        )
        return

    from audio_learning import render_audio_learning_panel

    icon = SPEC_ICONS.get(spec_id, "📘")

    if not inline:
        from session_state import close_workspace

        if st.button("← Back to Dashboard", key="back_to_dashboard"):
            close_workspace()
            st.rerun()
        st.markdown(
            f"""
            <div class="viewer-header">
              <h2>{icon} {lesson_title or title}</h2>
              <p>Multimodal workspace — read, listen, visualise, and interact.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("#### 🔊 Adaptive Audio Learning")

    auditory_mode = st.toggle(
        "Auditory Learning Mode",
        value=st.session_state.get("auditory_mode", False),
        help=(
            "Listening-first layout: larger, bolder lesson text (28px) and a taller "
            "audio transcript (30px) — ideal when you want to listen rather than read."
        ),
        key=f"auditory_toggle_{spec_id}",
    )
    st.session_state.auditory_mode = auditory_mode

    if auditory_mode:
        st.markdown(
            '<div class="alora-auditory-active" style="display:none;" aria-hidden="true"></div>',
            unsafe_allow_html=True,
        )

    render_accessibility_toolbar(spec_id)

    render_audio_learning_panel(
        title, content, spec_id, api_key, auditory_mode=auditory_mode, show_heading=False
    )

    st.markdown("---")
    st.markdown(f"#### 📚 {lesson_title or 'Lesson Content'}")

    st.markdown('<div class="adaptation-lesson-panel">', unsafe_allow_html=True)
    with st.container(border=True):
        if spec_id == "vocabulary":
            render_vocabulary(content, key_prefix=f"viewer_{spec_id}")
        elif spec_id == "worksheet":
            render_worksheet(content, key_prefix=f"viewer_{spec_id}")
        elif _coerce_dict(content):
            render_lesson(_coerce_dict(content), spec_id=spec_id)
        else:
            from content_renderer import render_rich_content

            render_rich_content(str(content))
    st.markdown("</div>", unsafe_allow_html=True)

    if not hide_downloads:
        render_viewer_downloads(
            title, content, spec_id, download_filename, zip_bytes, base_name
        )
