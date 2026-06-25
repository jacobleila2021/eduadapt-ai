"""
Accessibility tools — reading ruler, dyslexia-friendly text sizing.
"""

from __future__ import annotations

import streamlit as st

RULER_COLORS = {
    "Soft Yellow": "#FFF59D",
    "Soft Mint": "#A5D6A7",
    "Soft Aqua": "#80DEEA",
    "Soft Peach": "#FFAB91",
}


def get_accessibility_css(spec_id: str) -> str:
    color = st.session_state.get(f"ruler_color_{spec_id}", "Soft Yellow")
    opacity = float(st.session_state.get(f"ruler_opacity_{spec_id}", 0.45))
    width = int(st.session_state.get(f"ruler_width_{spec_id}", 100))
    height = int(st.session_state.get(f"ruler_height_{spec_id}", 48))
    font_px = int(st.session_state.get(f"lesson_font_{spec_id}", 22))
    hex_color = RULER_COLORS.get(color, "#FFF9C4")
    show_ruler = st.session_state.get(f"show_ruler_{spec_id}", False)

    ruler_html = ""
    if show_ruler:
        ruler_html = f"""
        <div class="alora-reading-ruler-{spec_id}" aria-hidden="true" style="
            position:fixed;left:50%;transform:translateX(-50%);
            width:{width}%;height:{height}px;background:{hex_color};
            opacity:{opacity};pointer-events:none;z-index:900;
            border-radius:8px;top:45%;"></div>
        """

    return f"""
    <style>
    .adaptation-lesson-panel {{
        font-size: {font_px}px !important;
        line-height: 1.85 !important;
        letter-spacing: 0.04em !important;
        font-family: "Atkinson Hyperlegible", "Comic Sans MS", Verdana, sans-serif !important;
        max-width: 100% !important;
        overflow-wrap: break-word !important;
        word-wrap: break-word !important;
    }}
    </style>
    {ruler_html}
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
            28,
            22,
            key=f"lesson_font_{spec_id}",
            help="Default 20–24px for dyslexia-friendly reading.",
        )

    st.markdown(get_accessibility_css(spec_id), unsafe_allow_html=True)


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
    .main .block-container:has(.alora-workspace-active)
    [data-testid="stHorizontalBlock"]:has([class*="st-key-subpill_"]) {
        position: fixed !important;
        bottom: 88px !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999990 !important;
        background: linear-gradient(180deg, #0a3d6e, #041B4D) !important;
        padding: 0.55rem 1.5rem !important;
        margin: 0 !important;
        box-shadow: 0 -4px 16px rgba(0,0,0,0.25) !important;
    }
    .adaptation-lesson-panel [data-testid="stVerticalBlockBorderWrapper"] {
        background: #fff !important;
        border-radius: 12px !important;
    }
    </style>
    """
