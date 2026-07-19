"""Render verified Computation / Answer Routing artifacts in Streamlit."""

from __future__ import annotations

from pathlib import Path

import streamlit as st


def render_preferred_visuals(meta: dict | None) -> None:
    """Show prioritized NCERT / engine visuals (before AI diagrams)."""
    if not meta or not isinstance(meta, dict):
        return
    preferred = meta.get("preferred_visuals") or []
    if not preferred:
        return

    st.markdown("### Verified Visuals (priority)")
    st.caption(
        "NCERT figures and engine assets take priority — AI must not invent competing diagrams."
    )
    for vis in preferred:
        source = vis.get("source") or "engine"
        caption = vis.get("caption") or source
        st.markdown(f"**[{source}]** {caption}")
        if vis.get("alt_text"):
            st.caption(vis["alt_text"])
        for path in vis.get("asset_paths") or []:
            p = Path(path)
            if p.is_file():
                st.image(str(p), caption=f"{source}: {caption}")
        if vis.get("iframe_url"):
            try:
                st.components.v1.iframe(vis["iframe_url"], height=360, scrolling=True)
            except Exception:
                st.markdown(f"[Open interactive]({vis['iframe_url']})")
        st.divider()


def render_verified_stem_panel(meta: dict | None) -> None:
    """Show engine-verified results (STEM + answer routing) above adaptations."""
    # Engine evidence is an internal QA concern, not classroom-facing content.
    if not st.session_state.get("show_internal_qa", False):
        return
    if not meta or not isinstance(meta, dict):
        return

    artifacts = meta.get("engine_artifacts") or []
    stem_qa = meta.get("stem_qa") or {}
    publish_qa = meta.get("publish_qa") or {}
    if not artifacts and not stem_qa and not meta.get("preferred_visuals"):
        return

    render_preferred_visuals(meta)

    st.markdown("### Verified Engines (Answer Routing)")
    if publish_qa.get("publish_blocked") or stem_qa.get("publish_blocked"):
        st.error(
            publish_qa.get("blocked_reason")
            or stem_qa.get("blocked_reason")
            or "Publish blocked — hard QA gate failed."
        )
    elif stem_qa.get("passed") is True and artifacts:
        st.success(
            f"{len(artifacts)} routed result(s) — AI must not invent STEM facts or MCQ keys."
        )
    elif artifacts:
        st.warning(
            stem_qa.get("blocked_reason")
            or "Some engine checks did not pass. Review before classroom use."
        )
    else:
        st.caption("No STEM / exam cues detected for engine routing.")

    for art in artifacts:
        kind = art.get("task_kind", "unknown")
        engine = art.get("engine_id", "engine")
        ok = art.get("ok", False)
        badge = "✓ Verified" if ok else "⚠ Check"
        st.markdown(f"**{badge}** · `{engine}` · {kind}")

        payload = art.get("payload") or {}
        for key, label in (
            ("balanced", "Balanced"),
            ("exact", "Result"),
            ("simplified", "Simplified"),
            ("formula", "Formula"),
            ("circuit_type", "Circuit"),
            ("geometry_kind", "Geometry"),
            ("diagram_type", "Physics diagram"),
            ("chart_type", "Chart"),
            ("official_answer", "Official answer"),
        ):
            if payload.get(key):
                st.caption(f"{label}: {payload[key]}")

        steps = payload.get("steps") or []
        if steps:
            with st.expander("Worked steps (SymPy)"):
                for s in steps[:10]:
                    st.markdown(f"- {s}")

        mistakes = payload.get("common_mistakes") or []
        if mistakes:
            st.caption("Common mistakes: " + "; ".join(str(m) for m in mistakes[:3]))

        if payload.get("citations"):
            st.caption("Citations: " + ", ".join(str(c) for c in payload["citations"][:6]))

        latex = art.get("latex")
        if latex:
            try:
                st.latex(latex)
            except Exception:
                st.code(latex)

        for path in art.get("asset_paths") or []:
            p = Path(path)
            if p.is_file():
                st.image(str(p), caption=f"Verified visual ({engine} · {kind})")

        iframe_url = payload.get("iframe_url")
        if iframe_url:
            st.caption("Interactive GeoGebra (requires network)")
            try:
                st.components.v1.iframe(iframe_url, height=420, scrolling=True)
            except Exception:
                st.markdown(f"[Open in GeoGebra]({iframe_url})")
            cmds = payload.get("commands") or []
            if cmds:
                with st.expander("GeoGebra commands"):
                    st.code("\n".join(cmds))

        matches = payload.get("matches") or []
        if matches:
            for m in matches[:3]:
                st.markdown(
                    f"- **{m.get('official_answer')}** — {m.get('question', '')[:100]} "
                    f"({m.get('source', '')})"
                )

        if art.get("error"):
            st.error(art["error"])

        st.divider()
