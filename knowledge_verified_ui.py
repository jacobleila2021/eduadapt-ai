"""Render Knowledge Layer citations and official MCQ bank in Streamlit."""

from __future__ import annotations

import streamlit as st


def render_knowledge_panel(meta: dict | None) -> None:
    # Provenance remains in _meta for QA/export; keep it off learner pages.
    if not st.session_state.get("show_internal_qa", False):
        return
    if not meta or not isinstance(meta, dict):
        return

    knowledge = meta.get("knowledge") or {}
    if not knowledge and not meta.get("engine_artifacts"):
        return

    st.markdown("### Verified Curriculum (Knowledge Layer)")
    if knowledge:
        st.caption(
            f"Pilot: **{knowledge.get('book_title', 'NCERT')}** · "
            f"{knowledge.get('board', 'CBSE')} Class {knowledge.get('grade', '')} "
            f"{knowledge.get('subject', '')}"
        )

        index = knowledge.get("index") or {}
        backend = index.get("backend", "unknown")
        st.info(
            f"RAG backend: **{backend}** · indexed chunks: **{index.get('indexed', 0)}** · "
            f"retrieved: **{len(knowledge.get('rag_hits') or [])}** · "
            f"official MCQs: **{len(knowledge.get('official_mcqs') or [])}**"
        )

        hits = knowledge.get("rag_hits") or []
        if hits:
            st.markdown("**NCERT citations (use in explanations)**")
            for hit in hits:
                st.markdown(f"- {hit.get('citation', '[NCERT]')} — *{hit.get('chapter_title', '')}*")
                excerpt = hit.get("excerpt") or ""
                if excerpt:
                    st.caption(excerpt[:280] + ("…" if len(excerpt) > 280 else ""))

        official = knowledge.get("official_mcqs") or []
        if official:
            st.markdown("**Official answer bank (keys not from LLM)**")
            for item in official:
                st.markdown(
                    f"- {item.get('citation', '')} · **Answer: {item.get('official_answer', '')}** — "
                    f"{item.get('question', '')[:120]}"
                )

        exam_bundle = knowledge.get("exam_bundle") or {}
        if any(exam_bundle.values()):
            st.markdown("**Exam question matching (Exemplar / PYQ / Sample / Competency / HOTS)**")
            for bkey, items in exam_bundle.items():
                if not items:
                    continue
                with st.expander(f"{bkey.replace('_', ' ').title()} ({len(items)})"):
                    for item in items:
                        st.markdown(
                            f"- [{item.get('source')}] {item.get('question', '')[:140]} "
                            f"→ **{item.get('official_answer', '')}** "
                            f"({item.get('marks', 1)}m · {item.get('bloom', '')})"
                        )

    st.markdown("### Teacher QA — Approve chapter facts")
    if meta.get("chapter_approved"):
        st.success(
            f"Using approved factual package `{meta.get('approved_package_id')}` "
            f"(approved {meta.get('approved_at', '')}). Presentation-only regeneration."
        )
    else:
        st.caption(
            "Validate STEM engines + NCERT citations once, then reuse facts for all learner versions."
        )
        if st.button("Approve chapter facts for reuse", key="approve_chapter_facts"):
            from knowledge.chapter_cache import approve_chapter_package

            ctx = meta.get("lesson_context") or {}
            topic = str(ctx.get("topic") or "Untitled chapter")
            package = approve_chapter_package(
                topic=topic,
                artifacts=meta.get("engine_artifacts") or [],
                preferred_visuals=meta.get("preferred_visuals") or [],
                biology_figures=meta.get("biology_figures") or [],
                knowledge=knowledge,
                stem_prompt_block="",
                approved_by="teacher",
                source_hash=str(
                    (meta.get("source_envelope") or {}).get("source_hash") or ""
                ),
            )
            meta["chapter_approved"] = True
            meta["approved_package_id"] = package.get("fingerprint")
            meta["approved_at"] = package.get("approved_at")
            st.success(f"Approved and cached: `{package.get('fingerprint')}`")
            st.rerun()
