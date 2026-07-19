"""
Dedicated adaptation workspace — separate from homepage dashboard.
"""

from __future__ import annotations

import re

import streamlit as st

from navigation import category_for_id
from print_exporter import build_print_html_all, build_print_html_single
from pill_tabs import render_pill_navigation, render_sub_spec_pills
from session_state import close_workspace
from lesson_design import lesson_title_html
from viewer_page import render_adaptation_viewer
from publication_gate import publication_block_reason

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
            help="Word (DOCX) for this tab only",
        )

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
    block_reason = publication_block_reason(
        adaptations,
        package=st.session_state.get("vlie_package"),
        quality=st.session_state.get("quality"),
    )
    if block_reason:
        st.error(
            "This lesson is quarantined and cannot be viewed or exported: "
            f"{block_reason}"
        )
        return

    spec_id = active_spec["id"]
    lesson_title = lesson_display_title()
    category_id = st.session_state.get("active_category_id", "")

    st.markdown(
        '<div class="alora-workspace-active" style="display:none;" aria-hidden="true"></div>',
        unsafe_allow_html=True,
    )

    st.button(
        "← Back to Dashboard",
        key="back_to_dashboard",
        type="secondary",
        on_click=close_workspace,
    )

    st.markdown(
        lesson_title_html(lesson_title, "Reading · Listening · Visual · Interactive", "introduction"),
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

    # Optional LXP Phases 1–2 chrome (default off — preserves existing viewer UX)
    use_lxp = st.toggle(
        "LXP Reader (Phases 1–2)",
        value=bool(st.session_state.get("lxp_reader_enabled", False)),
        key="lxp_reader_enabled",
        help="Premium reading workspace: themes, notes, progress, AI panel. Uses verified engines only.",
    )
    if use_lxp:
        from ui.lxp import render_lxp_reader

        generation_meta = (
            adaptations.get("_meta", {}) if isinstance(adaptations, dict) else {}
        )
        knowledge = generation_meta.get("knowledge") or {}
        context = generation_meta.get("lesson_context") or {}
        learner_id = str(st.session_state.get("learner_id") or st.session_state.get("user_id") or "anonymous")
        render_lxp_reader(
            lesson_text=lesson_text or "",
            topic=lesson_title or active_spec.get("title") or "",
            learner_id=learner_id,
            adaptations=adaptations if isinstance(adaptations, dict) else None,
            meta={
                "lesson_id": spec_id,
                "active_spec_id": spec_id,
                "active_spec_title": active_spec.get("title") or spec_id,
                "base_name": base_name,
                "api_key": api_key,
                "board": knowledge.get("board"),
                "grade": context.get("grade_level") or knowledge.get("grade"),
                "subject": knowledge.get("subject"),
                "chapter": knowledge.get("chapter"),
                "curriculum_resolution": generation_meta.get(
                    "curriculum_resolution"
                )
                or {},
                "pipeline_result": generation_meta.get("pipeline_result") or {},
            },
        )
    else:
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
