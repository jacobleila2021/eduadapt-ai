"""Meaningful loading states — skeletons & retries."""

from __future__ import annotations

import streamlit as st


def render_skeleton(label: str = "Loading lesson…") -> None:
    st.markdown(
        f"""
        <div class="lxp-premium" aria-busy="true" aria-label="{label}">
          <div style="height:14px;width:40%;background:rgba(0,0,0,.06);border-radius:4px;margin:.4rem 0;"></div>
          <div style="height:10px;width:92%;background:rgba(0,0,0,.05);border-radius:4px;margin:.35rem 0;"></div>
          <div style="height:10px;width:88%;background:rgba(0,0,0,.05);border-radius:4px;margin:.35rem 0;"></div>
          <div style="height:120px;width:100%;background:rgba(0,0,0,.04);border-radius:6px;margin:.6rem 0;"
               aria-label="Diagram placeholder"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_ai_pending() -> None:
    st.caption("AI panel · retrieving verified context…")


def render_offline_loading() -> None:
    st.info("Loading from offline package…")


def render_retry(key: str = "lxp4_retry") -> bool:
    return st.button("Retry", key=key)
