"""
Dedicated adaptation workspace — separate from homepage dashboard.
"""

from __future__ import annotations

import re

import streamlit as st

from accessibility import get_workspace_layout_css
from navigation import category_for_id
from print_exporter import build_print_html_all, build_print_html_single
from pill_tabs import render_pill_navigation, render_sub_spec_pills
from session_state import close_workspace
from spec_icons import SPEC_ICONS
from viewer_page import render_adaptation_viewer

_TITLE_NOISE = re.compile(
    r"\b(lesson|grade|class|year|student|learner|adapted?|adaptation|version|final|draft|copy|v\d+|worksheet|notes?|sample|demo|test|placeholder|example|untitled|document|doc|file)\b",
    re.IGNORECASE,
)


def _clean_title(raw: str) -> str:
    text = (raw or "").replace("_", " ").replace("-", " ")
    # Drop subtitle after a colon, e.g. "The Water Cycle: How Water Moves" -> "The Water Cycle"
    if ":" in text:
        text = text.split(":", 1)[0]
    cleaned = _TITLE_NOISE.sub(" ", text)
    cleaned = re.sub(r"\d+", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .,:-")
    # Keep it short and professional (max 5 words).
    words = cleaned.split()
    return " ".join(words[:5]).title()


def lesson_display_title() -> str:
    """Actual lesson topic only — prefer AI-detected topic, never the filename 'Sample'."""
    adaptations = st.session_state.get("adaptations") or {}
    meta = adaptations.get("_meta", {}) if isinstance(adaptations, dict) else {}
    ctx = meta.get("lesson_context") or {}

    # 1. AI-detected topic (most reliable, e.g. "Water Cycle")
    topic = (ctx.get("topic") or "").strip()
    # 2. Vocabulary topic
    if not topic:
        vocab = adaptations.get("vocabulary") if isinstance(adaptations, dict) else None
        if isinstance(vocab, dict):
            topic = (vocab.get("topic") or "").strip()
    if topic and topic.lower() not in {"lesson", "lesson vocabulary", "topic", "subject"}:
        return _clean_title(topic) or "Your Lesson"

    # 3. Fall back to a cleaned upload filename (strips sample/demo/test/etc.)
    cleaned = _clean_title(st.session_state.get("upload_name", ""))
    return cleaned or "Your Lesson"


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

    st.markdown("#### Download & Print")
    st.caption(
        "**This version** = Word or print-ready HTML for the tab you are viewing only. "
        "**All adaptations** = combined pack with cover page and table of contents. "
        "Exam Worksheet Word files are student papers only (no answer key)."
    )
    c1, c2, c3, c4 = st.columns(4)

    docx_bytes = export_tab_docx(title, content, spec_id)
    print_single = build_print_html_single(title, content, spec_id)
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
            key=f"ws_dl_this_{spec_id}",
            help="Word (DOCX) for this tab only — student worksheet has no answer key",
        )
        st.caption("MP3 audio is in the Audio Learning section below.")

    with c2:
        if zip_bytes:
            st.download_button(
                "Download All Adaptations",
                data=zip_bytes,
                file_name=f"{base_name}_alora_print_pack.zip",
                mime="application/zip",
                use_container_width=True,
                key="ws_dl_all_zip",
                help="ZIP with HTML + Word per version",
            )
        st.download_button(
            "Combined HTML Pack",
            data=print_all,
            file_name=f"{base_name}_all_adaptations.html",
            mime="text/html",
            use_container_width=True,
            key="ws_dl_all_html",
        )

    with c3:
        st.download_button(
            "Print This Version",
            data=print_single,
            file_name=f"{base_name}_{spec_id}_print.html",
            mime="text/html",
            use_container_width=True,
            key=f"ws_print_this_{spec_id}",
            help="Single-version print layout — open file, then Ctrl+P",
        )

    with c4:
        st.download_button(
            "Print All Adaptations",
            data=print_all,
            file_name=f"{base_name}_print_all.html",
            mime="text/html",
            use_container_width=True,
            key="ws_print_all_pack",
            help="Cover + contents + all 9 versions — open file, then Ctrl+P",
        )


def render_bottom_adaptation_bar(category_id: str, active_spec_id: str) -> None:
    """Fixed bottom bar — sub-version pills + category pills."""
    st.markdown(
        '<p class="bottom-tabs-label">Switch adaptation version</p>',
        unsafe_allow_html=True,
    )
    category = category_for_id(category_id)
    if category and len(category["spec_ids"]) > 1:
        render_sub_spec_pills(category_id, active_spec_id)
    render_pill_navigation(key_prefix="ws_pill")


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
    lesson_title = lesson_display_title()
    category_id = st.session_state.get("active_category_id", "")

    st.markdown(
        '<div class="alora-workspace-active" style="display:none;"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(get_workspace_layout_css(), unsafe_allow_html=True)

    st.button(
        "← Back to Dashboard",
        key="back_to_dashboard",
        type="secondary",
        on_click=close_workspace,
    )

    st.markdown(
        '<div class="workspace-mode-strip">Adaptation workspace — one version at a time</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="workspace-banner">
          <h2>{icon} {lesson_title}</h2>
          <p>Reading · Listening · Visual · Interactive</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
        lesson_title=lesson_title,
    )

    render_bottom_adaptation_bar(category_id, spec_id)
