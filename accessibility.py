"""
Accessibility tools — reading ruler, dyslexia-friendly text sizing.
"""

from __future__ import annotations

import json

import streamlit as st
import streamlit.components.v1 as components

RULER_COLORS = {
    "Soft Yellow": "#FFF59D",
    "Soft Mint": "#A5D6A7",
    "Soft Aqua": "#80DEEA",
    "Soft Peach": "#FFAB91",
}


def get_accessibility_css(spec_id: str) -> str:
    """Font-size CSS scoped to the workspace via a hidden marker class."""
    font_px = int(st.session_state.get(f"lesson_font_{spec_id}", 22))
    marker = f"alora-a11y-{spec_id}"
    return f"""
    <style>
    .main .block-container:has(.{marker}) [data-testid="stMarkdownContainer"] p,
    .main .block-container:has(.{marker}) [data-testid="stMarkdownContainer"] li,
    .main .block-container:has(.{marker}) [data-testid="stMarkdownContainer"] span,
    .main .block-container:has(.{marker}) [data-testid="stMarkdownContainer"] td,
    .main .block-container:has(.{marker}) [data-testid="stMarkdownContainer"] th,
    .main .block-container:has(.{marker}) [data-testid="stMarkdownContainer"] h1,
    .main .block-container:has(.{marker}) [data-testid="stMarkdownContainer"] h2,
    .main .block-container:has(.{marker}) [data-testid="stMarkdownContainer"] h3,
    .main .block-container:has(.{marker}) [data-testid="stMarkdownContainer"] h4,
    .main .block-container:has(.{marker}) .stAlert p,
    .main .block-container:has(.{marker}) [data-testid="stTextArea"] textarea,
    .main .block-container:has(.{marker}) [data-testid="stTextInput"] input {{
        font-size: {font_px}px !important;
        line-height: 1.85 !important;
        letter-spacing: 0.04em !important;
        font-family: "Atkinson Hyperlegible", "Comic Sans MS", Verdana, sans-serif !important;
    }}
    </style>
    <div class="{marker}" style="display:none;" aria-hidden="true"></div>
    """


def _reading_ruler_html(spec_id: str) -> str:
    """Mouse-following reading ruler overlay (works across the whole page)."""
    show = st.session_state.get(f"show_ruler_{spec_id}", False)
    color_name = st.session_state.get(f"ruler_color_{spec_id}", "Soft Yellow")
    opacity = float(st.session_state.get(f"ruler_opacity_{spec_id}", 0.45))
    width = int(st.session_state.get(f"ruler_width_{spec_id}", 100))
    height = int(st.session_state.get(f"ruler_height_{spec_id}", 48))
    hex_color = RULER_COLORS.get(color_name, "#FFF59D")

    return f"""
    <div id="alora-ruler-root" style="position:fixed;inset:0;pointer-events:none;z-index:9999;">
      <div id="alora-ruler-bar" style="
        display:{'block' if show else 'none'};
        position:fixed;left:50%;transform:translateX(-50%);
        width:{width}%;height:{height}px;background:{hex_color};
        opacity:{opacity};border-radius:8px;pointer-events:none;
        top:40%;"></div>
    </div>
    <script>
    (function() {{
      const bar = document.getElementById("alora-ruler-bar");
      if (!bar) return;
      document.addEventListener("mousemove", function(e) {{
        if (bar.style.display === "none") return;
        const h = bar.offsetHeight || {height};
        bar.style.top = Math.max(0, e.clientY - h / 2) + "px";
      }});
    }})();
    </script>
    """


def render_accessibility_toolbar(spec_id: str) -> None:
    """Reading ruler + font size controls."""
    with st.expander("♿ Reading Ruler & Text Size", expanded=False):
        st.checkbox("Show reading ruler overlay", key=f"show_ruler_{spec_id}")
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox(
                "Ruler colour",
                list(RULER_COLORS.keys()),
                key=f"ruler_color_{spec_id}",
            )
            st.slider("Ruler opacity", 0.2, 0.9, 0.45, 0.05, key=f"ruler_opacity_{spec_id}")
        with c2:
            st.slider("Ruler width %", 60, 100, 100, key=f"ruler_width_{spec_id}")
            st.slider("Ruler height (px)", 32, 80, 48, key=f"ruler_height_{spec_id}")
        st.slider(
            "Text size (px)",
            18,
            32,
            22,
            key=f"lesson_font_{spec_id}",
            help="Applies to lesson text below. Move the slider and the page updates instantly.",
        )
        st.caption(
            "Tip: turn on the ruler, then move your mouse — the highlight band follows "
            "your reading line."
        )

    st.markdown(get_accessibility_css(spec_id), unsafe_allow_html=True)
    components.html(_reading_ruler_html(spec_id), height=0)


def get_workspace_layout_css() -> str:
    """Bottom tab bar + content padding — workspace only."""
    return """
    <style>
    .main .block-container:has(.alora-workspace-active) {
        padding-bottom: 280px !important;
    }
    .main .block-container:has(.alora-workspace-active)
    [data-testid="stHorizontalBlock"]:has([class*="st-key-ws_pill_"]) {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999991 !important;
        background: linear-gradient(180deg, #041B4D, #031638) !important;
        padding: 0.75rem 1.5rem 1rem 1.5rem !important;
        margin: 0 !important;
        box-shadow: 0 -8px 28px rgba(0,0,0,0.35) !important;
        max-width: 100vw !important;
    }
    .adaptation-lesson-panel [data-testid="stVerticalBlockBorderWrapper"] {
        background: #fff !important;
        border-radius: 12px !important;
    }
    </style>
    """
