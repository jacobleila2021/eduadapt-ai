"""
Adaptation pill tabs — opens dedicated workspace on click.
on_click callbacks run before the rest of the script (keeps adaptations intact).
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from navigation import PILL_CATEGORIES, category_for_id, category_for_spec, spec_by_id
from session_state import VIEW_WORKSPACE, is_workspace, open_adaptation


def _pill_instant_highlight_html() -> str:
    """Instant active-tab feedback via parent document (Streamlit blocks script in st.markdown)."""
    return """
    <script>
    (function () {
      function pageDoc() {
        var candidates = [window.top, window.parent, window];
        for (var i = 0; i < candidates.length; i++) {
          try {
            if (candidates[i] && candidates[i].document && candidates[i].document.body) {
              return candidates[i].document;
            }
          } catch (e) {}
        }
        return document;
      }
      var d = pageDoc();
      if (d.__aloraPillBound) return;
      d.__aloraPillBound = true;
      function highlightPill(btn) {
        var root = btn.closest(".main") || d;
        root.querySelectorAll(
          '[class*="st-key-ws_pill_"] button[kind="primary"], ' +
          '[class*="st-key-pill_"] button[kind="primary"], ' +
          '[class*="st-key-subpill_"] button[kind="primary"]'
        ).forEach(function (el) {
          el.setAttribute("kind", "secondary");
        });
        btn.setAttribute("kind", "primary");
      }
      d.addEventListener("pointerdown", function (event) {
        var btn = event.target.closest(
          '[class*="st-key-ws_pill_"] button, [class*="st-key-pill_"] button, [class*="st-key-subpill_"] button'
        );
        if (btn) highlightPill(btn);
      }, true);
    })();
    </script>
    """


def inject_pill_instant_highlight() -> None:
    """Hidden iframe script — must not use st.markdown (scripts render as visible text)."""
    components.html(_pill_instant_highlight_html(), height=0, scrolling=False)


def _open_category(category_id: str) -> None:
    open_adaptation(category_id)


def _open_spec(spec_id: str) -> None:
    st.session_state.active_output_id = spec_id
    cat = category_for_spec(spec_id)
    if cat:
        st.session_state.active_category_id = cat["id"]
    st.session_state.app_view = VIEW_WORKSPACE


def render_pill_navigation(key_prefix: str = "pill") -> None:
    """Dark cyan pills — one click opens the dedicated workspace."""
    active_cat = st.session_state.get("active_category_id", "")
    in_workspace = is_workspace()

    cols_per_row = 3
    for row_start in range(0, len(PILL_CATEGORIES), cols_per_row):
        row = PILL_CATEGORIES[row_start : row_start + cols_per_row]
        cols = st.columns(cols_per_row)
        for col, category in zip(cols, row):
            with col:
                cat_id = category["id"]
                is_active = in_workspace and active_cat == cat_id
                st.button(
                    category["label"],
                    key=f"{key_prefix}_{cat_id}",
                    use_container_width=True,
                    type="primary" if is_active else "secondary",
                    on_click=_open_category,
                    kwargs={"category_id": cat_id},
                )
        for col in cols[len(row) :]:
            with col:
                st.empty()


def render_sub_spec_pills(category_id: str, active_spec_id: str) -> None:
    """Secondary pills for categories with multiple versions."""
    category = category_for_id(category_id)
    if not category or len(category["spec_ids"]) <= 1:
        return

    st.markdown("**Versions in this category**")
    spec_ids = category["spec_ids"]
    cols = st.columns(min(len(spec_ids), 5))
    for col, spec_id in zip(cols, spec_ids):
        spec = spec_by_id(spec_id)
        if not spec:
            continue
        with col:
            st.button(
                spec["tab"],
                key=f"subpill_{spec_id}",
                use_container_width=True,
                type="primary" if spec_id == active_spec_id else "secondary",
                on_click=_open_spec,
                kwargs={"spec_id": spec_id},
            )
