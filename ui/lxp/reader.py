"""Streamlit UI shell for LXP Phases 1–2 — wraps existing viewer/audio/a11y."""

from __future__ import annotations

import logging
from typing import Any

import streamlit as st

logger = logging.getLogger(__name__)

from engines.learning_experience_platform.service import (
    api_add_bookmark,
    api_add_highlight,
    api_add_note,
    api_apply_accessibility,
    api_get_preferences,
    api_list_bookmarks,
    api_list_highlights,
    api_list_notes,
    api_open_reader,
    api_update_preferences,
    api_update_progress,
)


def render_lxp_reader(
    *,
    lesson_text: str,
    topic: str = "",
    learner_id: str = "anonymous",
    adaptations: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Premium LXP chrome around the existing adaptation viewer.

    Does not replace viewer_page rendering of lesson body — adds Phase 1/2 panels.
    """
    meta = meta or {}
    pipeline_result = meta.get("pipeline_result") or {}
    if pipeline_result.get("status") in {"failed", "blocked"}:
        st.error(
            f"**{str(pipeline_result.get('stage') or 'Reader').replace('_', ' ').title()}** — "
            f"{pipeline_result.get('message') or 'This lesson is not available.'}"
        )
        if pipeline_result.get("recovery"):
            st.info(f"Recovery: {pipeline_result['recovery']}")
        return {
            "ok": False,
            "pipeline_result": pipeline_result,
            "fallback_used": pipeline_result.get("fallback_used") or "none",
        }
    curriculum = meta.get("curriculum_resolution") or {}
    if curriculum.get("status") == "unknown":
        st.caption("Curriculum: Unknown / source-grounded")
    session = api_open_reader(
        learner_id=learner_id,
        lesson_text=lesson_text,
        topic=topic,
        lesson={"title": topic or "Lesson", "body": lesson_text, "lesson_id": meta.get("lesson_id") or topic or "lesson"},
        board=meta.get("board"),
        grade=meta.get("grade"),
        subject=meta.get("subject"),
        chapter=meta.get("chapter"),
    )
    lesson_id = session.get("lesson_id") or "lesson"
    prefs = api_get_preferences(learner_id)["preferences"]
    theme = session.get("layout", {}).get("theme", {}).get("tokens") or {}

    # Phase 4 — premium chrome (motion/a11y/PWA hints; never blocks content)
    try:
        from ui.learning_experience_platform.premium import inject_premium_chrome

        inject_premium_chrome(learner_id=learner_id)
    except Exception:
        pass

    st.markdown(
        f"""
        <style>
        .lxp-shell {{
          --lxp-bg: {theme.get('bg', '#FAFAF8')};
          --lxp-fg: {theme.get('fg', '#1A1A1A')};
          --lxp-panel: {theme.get('panel', '#fff')};
          --lxp-accent: {theme.get('accent', '#2F6F5E')};
          background: var(--lxp-bg); color: var(--lxp-fg);
        }}
        .lxp-toolbar {{
          position: sticky; top: 0; z-index: 20;
          background: var(--lxp-panel); border-bottom: 1px solid rgba(0,0,0,.08);
          padding: .5rem .75rem; display:flex; gap:.5rem; flex-wrap:wrap; align-items:center;
        }}
        .lxp-footer {{
          position: sticky; bottom: 0; background: var(--lxp-panel);
          border-top: 1px solid rgba(0,0,0,.08); padding: .4rem .75rem; font-size: .85rem;
        }}
        </style>
        <div class="lxp-shell"></div>
        """,
        unsafe_allow_html=True,
    )

    # Sticky toolbar
    crumbs = " › ".join(f"{c['label']}: {c['value']}" for c in (session.get("layout") or {}).get("breadcrumbs") or [])
    st.caption(crumbs or "LXP Reader")
    t1, t2, t3, t4, t5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.5])
    with t1:
        theme_name = st.selectbox("Theme", ["light", "dark", "sepia", "high_contrast"], index=["light", "dark", "sepia", "high_contrast"].index(prefs.get("theme") or "light"))
    with t2:
        mode = st.selectbox("Mode", ["continuous_scroll", "paged", "focus", "fullscreen"], index=0)
    with t3:
        font_px = st.slider("Font size", 14, 32, int(prefs.get("font_size_px") or 18))
    with t4:
        if st.button("Apply a11y"):
            api_apply_accessibility(learner_id)
            st.toast("Accessibility preferences applied")
    with t5:
        pct = st.slider("Reading %", 0, 100, int(float((session.get("progress") or {}).get("reading_pct") or 0)))
        if st.button("Save progress"):
            api_update_progress(learner_id, lesson_id, reading_pct=float(pct), lesson_text=lesson_text, delta_seconds=30)
            st.toast("Progress saved")

    api_update_preferences(learner_id, {"theme": theme_name, "reading_mode": mode, "font_size_px": font_px})

    left, main, right = st.columns([1.1, 2.4, 1.3] if prefs.get("split_ai_panel", True) else [1.1, 3.7, 0.01])

    with left:
        st.subheader("Contents")
        for item in ((session.get("layout") or {}).get("navigation") or {}).get("toc") or []:
            st.markdown(f"- [{item.get('title')}](#{item.get('anchor')})")
        st.subheader("Bookmarks")
        for b in api_list_bookmarks(learner_id)["bookmarks"][-5:]:
            st.caption(f"{b.get('folder')}: {b.get('label') or b.get('anchor')}")
        if st.button("Bookmark here"):
            api_add_bookmark(learner_id, lesson_id=lesson_id, label=topic or "Here", anchor="sec_0")
            st.toast("Bookmarked")

    with main:
        st.subheader(topic or "Lesson")
        # Reuse existing viewer for adaptation body when available
        if adaptations:
            try:
                from viewer_page import render_adaptation_viewer

                spec_id = meta.get("active_spec_id") or next(
                    (k for k in adaptations if not str(k).startswith("_")), None
                )
                if spec_id:
                    active_content = adaptations.get(spec_id)
                    active_title = str(
                        meta.get("active_spec_title") or spec_id.replace("_", " ").title()
                    )
                    render_adaptation_viewer(
                        spec_id=str(spec_id),
                        title=active_title,
                        content=active_content,
                        download_filename=f"{meta.get('base_name') or 'lesson'}_{spec_id}.txt",
                        zip_bytes=None,
                        base_name=str(meta.get("base_name") or "lesson"),
                        api_key=str(meta.get("api_key") or ""),
                        inline=True,
                        hide_downloads=True,
                        lesson_title=topic,
                    )
                else:
                    st.write(lesson_text)
            except Exception:
                logger.exception("LXP adaptation viewer failed")
                st.error("The premium reader could not display this adaptation.")
        else:
            st.write(lesson_text)

        with st.expander("Notes & highlights"):
            note_text = st.text_area("New note", key=f"lxp_note_{lesson_id}")
            if st.button("Save note") and note_text.strip():
                api_add_note(learner_id, lesson_id=lesson_id, text=note_text.strip(), category="general")
                st.toast("Note saved")
            for n in api_list_notes(learner_id, lesson_id)[-8:]:
                st.markdown(f"- **{n.get('category')}**: {n.get('text')}")
            color = st.selectbox("Highlight color", ["yellow", "green", "blue", "pink"])
            excerpt = st.text_input("Highlight excerpt")
            if st.button("Add highlight") and excerpt.strip():
                api_add_highlight(learner_id, lesson_id=lesson_id, color=color, excerpt=excerpt.strip(), target_type="text")
                st.toast("Highlight added")
            for h in api_list_highlights(learner_id, lesson_id)[-8:]:
                st.caption(f"[{h.get('color')}] {h.get('excerpt')}")

    if prefs.get("split_ai_panel", True):
        with right:
            st.subheader("AI panel")
            phase2 = session.get("phase2") or {}
            st.caption("ATIE · VMLE · ALCIS · LMAS")
            if phase2.get("summary", {}).get("key_ideas"):
                st.markdown("**Key ideas**")
                for idea in phase2["summary"]["key_ideas"][:4]:
                    st.write(f"• {str(idea)[:160]}")
            mot = phase2.get("motivation") or {}
            if mot.get("ok"):
                xp = ((mot.get("xp") or {}).get("xp_total"))
                st.metric("XP", xp if xp is not None else "—")
            if st.button("Refresh companion nudge"):
                st.json((phase2.get("companion") or {}).get("behaviors") or [])

    # Phase 3 — collaboration, revision, assessment (unified LXP)
    with st.expander("LXP Phase 3 — Collaboration · Revision · Assessment", expanded=False):
        from ui.learning_experience_platform import render_phase3_panel

        role = str((meta or {}).get("role") or st.session_state.get("lxp_role") or "student")
        render_phase3_panel(
            learner_id=learner_id,
            lesson_id=lesson_id,
            lesson={"title": topic, "body": lesson_text, "lesson_id": lesson_id, "word_wall": (meta or {}).get("word_wall") or []},
            topic=topic,
            role=role,
            context={"subject": (meta or {}).get("subject"), "role": role, **(meta or {})},
        )

    # Phase 4 — premium settings / sync / PWA
    with st.expander("LXP Phase 4 — Premium · Sync · Accessibility", expanded=False):
        try:
            from ui.learning_experience_platform.premium import render_premium_panel

            render_premium_panel(learner_id=learner_id)
        except Exception:
            logger.exception("LXP premium panel failed")
            st.caption("Premium settings are temporarily unavailable.")

    # Footer progress
    prog = session.get("progress") or {}
    st.markdown(
        f'<div class="lxp-footer">Progress {float(prog.get("reading_pct") or 0):.0f}% · '
        f'Est. {prog.get("estimated_minutes") or session.get("estimated_reading_minutes") or 0} min · '
        f'Time {float(prog.get("time_spent_seconds") or 0):.0f}s</div>',
        unsafe_allow_html=True,
    )
    return session
