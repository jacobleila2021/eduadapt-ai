"""Collaboration UI — comments & shared annotations."""

from __future__ import annotations

import streamlit as st

from engines.learning_experience_platform.service import (
    api_add_comment,
    api_list_comments,
    api_list_shared_annotations,
    api_shared_annotation,
)


def render_collaboration(*, lesson_id: str, user_id: str, role: str = "student") -> None:
    st.subheader("Collaboration")
    body = st.text_area("Comment", key=f"lxp3_c_{lesson_id}")
    audience = st.selectbox("Audience", ["class", "selected_students", "parents", "special_educators"], disabled=role not in ("teacher", "administrator"))
    if st.button("Post comment", key=f"lxp3_post_{lesson_id}") and body.strip():
        out = api_add_comment(
            lesson_id=lesson_id,
            author_id=user_id,
            author_role=role,
            body=body.strip(),
            audience=audience if role == "teacher" else ("class" if role == "student" else "parents"),
        )
        if out.get("ok"):
            st.toast("Comment posted")
        else:
            st.warning(out.get("denied") or out.get("error") or "Not allowed")

    comments = api_list_comments(lesson_id=lesson_id, viewer_id=user_id, viewer_role=role, threaded=True)
    for t in comments.get("threads") or comments.get("comments") or []:
        st.markdown(f"**{t.get('author_role')}**: {t.get('body')}")
        for r in t.get("replies") or []:
            st.caption(f"↳ {r.get('author_role')}: {r.get('body')}")

    with st.expander("Shared annotations"):
        excerpt = st.text_input("Annotation text", key=f"lxp3_ann_{lesson_id}")
        vis = st.selectbox("Visibility", ["private", "teacher_only", "shared_classroom", "parent_only", "special_educator"])
        if st.button("Add annotation") and excerpt.strip():
            api_shared_annotation(
                lesson_id=lesson_id,
                author_id=user_id,
                author_role=role,
                annotation_type="sticky_note",
                visibility=vis if role != "student" else "private",
                payload={"text": excerpt.strip()},
            )
            st.toast("Annotation saved")
        for a in api_list_shared_annotations(lesson_id=lesson_id, viewer_id=user_id, viewer_role=role).get("annotations") or []:
            st.caption(f"v{a.get('version')} [{a.get('visibility')}] {(a.get('payload') or {}).get('text')}")
