"""
Dedicated adaptation workspace — separate from homepage dashboard.
"""

from __future__ import annotations

import streamlit as st

from print_exporter import build_print_html_all, build_print_html_single
from session_state import close_workspace, open_adaptation
from spec_icons import SPEC_ICONS
from viewer_page import render_adaptation_viewer


def render_workspace_pills() -> None:
    """Switch adaptation while staying in workspace."""
    from pill_tabs import render_pill_navigation as _render_pills

    _render_pills(key_prefix="ws_pill")


def render_action_bar(
    title: str,
    content,
    spec_id: str,
    download_filename: str,
    zip_bytes: bytes | None,
    base_name: str,
    adaptations: dict,
    lesson_text: str,
    content_for_spec,
) -> None:
    """Four premium actions: download/print this version and all."""
    from docx_exporter import export_tab_docx
    from html_exporter import export_tab_html as rich_html_export
    from audio_learning import OPENAI_VOICE_MAP, extract_speech_text, generate_openai_speech

    st.markdown("#### Download & Print")
    c1, c2, c3, c4 = st.columns(4)

    docx_bytes = export_tab_docx(title, content, spec_id)
    html_bytes = rich_html_export(title, content, spec_id)
    print_single = build_print_html_single(title, content, spec_id)

    api_key = st.session_state.get("runtime_api_key", "")
    voice = st.session_state.get("audio_voice", "Female Professional")
    speech = extract_speech_text(title, content, spec_id)
    mp3 = generate_openai_speech(speech, OPENAI_VOICE_MAP.get(voice, "nova"), api_key)

    print_all = build_print_html_all(
        adaptations, lesson_text, base_name, content_for_spec
    )

    with c1:
        st.download_button(
            "Download This Version",
            data=docx_bytes,
            file_name=download_filename.rsplit(".", 1)[0] + ".docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key=f"dl_this_{spec_id}",
            help="Word (DOCX) with LD-friendly formatting",
        )
        if mp3:
            st.download_button(
                "MP3 Audio",
                data=mp3,
                file_name=f"{base_name}_{spec_id}.mp3",
                mime="audio/mpeg",
                use_container_width=True,
                key=f"dl_mp3_{spec_id}",
            )

    with c2:
        if zip_bytes:
            st.download_button(
                "Download All Adaptations",
                data=zip_bytes,
                file_name=f"{base_name}_alora_print_pack.zip",
                mime="application/zip",
                use_container_width=True,
                key="dl_all_zip",
                help="ZIP with HTML + Word per version",
            )
        st.download_button(
            "Combined HTML Pack",
            data=print_all,
            file_name=f"{base_name}_all_adaptations.html",
            mime="text/html",
            use_container_width=True,
            key="dl_all_html",
        )

    with c3:
        st.download_button(
            "Print This Version",
            data=print_single,
            file_name=f"{base_name}_{spec_id}_print.html",
            mime="text/html",
            use_container_width=True,
            key=f"print_this_{spec_id}",
            help="Download print-ready HTML — open and press Ctrl+P",
        )

    with c4:
        st.download_button(
            "Print All Adaptations",
            data=print_all,
            file_name=f"{base_name}_print_all.html",
            mime="text/html",
            use_container_width=True,
            key="print_all_pack",
            help="Cover page, contents, and all primary versions",
        )


def render_workspace(
    active_spec: dict,
    content,
    download_filename: str,
    zip_bytes: bytes | None,
    base_name: str,
    api_key: str,
    adaptations: dict,
    lesson_text: str,
    content_for_spec,
) -> None:
    """Full-screen dedicated workspace for one adaptation."""
    spec_id = active_spec["id"]
    icon = SPEC_ICONS.get(spec_id, "📘")

    st.button(
        "← Back to Dashboard",
        key="back_to_dashboard",
        type="secondary",
        on_click=close_workspace,
    )

    st.markdown(
        f"""
        <div class="workspace-banner">
          <h2>{icon} {active_spec["title"]}</h2>
          <p>Dedicated adaptation workspace — Reading · Listening · Visual · Interactive</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_workspace_pills()

    render_action_bar(
        active_spec["title"],
        content,
        spec_id,
        download_filename,
        zip_bytes,
        base_name,
        adaptations,
        lesson_text,
        content_for_spec,
    )

    render_adaptation_viewer(
        spec_id=spec_id,
        title=active_spec["title"],
        content=content,
        download_filename=download_filename,
        zip_bytes=zip_bytes,
        base_name=base_name,
        api_key=api_key,
        inline=True,
        hide_downloads=True,
    )
