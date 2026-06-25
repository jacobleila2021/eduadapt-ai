"""
Accessibility tools — reading ruler, dyslexia-friendly text sizing.
"""

from __future__ import annotations

import streamlit as st

RULER_COLORS = {
    "Soft Yellow": "#FFF9C4",
    "Light Aqua": "#B2EBF2",
    "Soft Mint": "#C8E6C9",
    "Light Peach": "#FFCCBC",
}


def get_accessibility_css(spec_id: str) -> str:
    color = st.session_state.get(f"ruler_color_{spec_id}", "Soft Yellow")
    opacity = float(st.session_state.get(f"ruler_opacity_{spec_id}", 0.45))
    width = int(st.session_state.get(f"ruler_width_{spec_id}", 100))
    height = int(st.session_state.get(f"ruler_height_{spec_id}", 48))
    font_px = int(st.session_state.get(f"lesson_font_{spec_id}", 22))
    hex_color = RULER_COLORS.get(color, "#FFF9C4")

    return f"""
    <style>
    .lesson-content-panel-{spec_id} {{
        font-size: {font_px}px !important;
        line-height: 1.85 !important;
        letter-spacing: 0.04em !important;
        font-family: "Atkinson Hyperlegible", "Comic Sans MS", Verdana, sans-serif !important;
    }}
    .lesson-content-panel-{spec_id} p,
    .lesson-content-panel-{spec_id} li,
    .lesson-content-panel-{spec_id} span {{
        font-size: {font_px}px !important;
    }}
    .alora-reading-ruler-{spec_id} {{
        position: fixed;
        left: 50%;
        transform: translateX(-50%);
        width: {width}%;
        height: {height}px;
        background: {hex_color};
        opacity: {opacity};
        pointer-events: none;
        z-index: 99990;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(51,65,85,0.15);
        top: 45%;
    }}
    .main .block-container:has(.lesson-content-panel-{spec_id}) {{
        padding-bottom: 240px;
    }}
    [data-testid="stHorizontalBlock"]:has([class*="st-key-ws_pill_"]),
    [data-testid="stHorizontalBlock"]:has([class*="st-key-subpill_"]) {{
        position: fixed !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999991 !important;
        background: linear-gradient(180deg, #334155, #1e293b) !important;
        padding: 0.65rem 1.25rem !important;
        margin: 0 !important;
        box-shadow: 0 -6px 24px rgba(0,0,0,0.28) !important;
    }}
    [data-testid="stHorizontalBlock"]:has([class*="st-key-subpill_"]) {{
        bottom: 72px !important;
    }}
    [data-testid="stHorizontalBlock"]:has([class*="st-key-ws_pill_"]) {{
        bottom: 0 !important;
    }}
    </style>
    <div class="alora-reading-ruler-{spec_id}" aria-hidden="true"></div>
    """


def render_accessibility_toolbar(spec_id: str) -> None:
    """Reading ruler + font size controls."""
    with st.expander("♿ Reading Ruler & Text Size", expanded=False):
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
            28,
            22,
            key=f"lesson_font_{spec_id}",
            help="Default 20–24px for dyslexia-friendly reading.",
        )

    st.markdown(get_accessibility_css(spec_id), unsafe_allow_html=True)
