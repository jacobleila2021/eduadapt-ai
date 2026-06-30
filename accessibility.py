"""
Accessibility tools — reading ruler, dyslexia-friendly text sizing.
CSS lives in styles.py; this module only sets dynamic CSS variables via hidden markers.
"""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

RULER_COLORS = {
    "Soft Yellow": "#FFF59D",
    "Soft Mint": "#A5D6A7",
    "Soft Aqua": "#80DEEA",
    "Soft Peach": "#FFAB91",
}


def _a11y_marker_html(spec_id: str) -> str:
    """Hidden marker that sets --alora-font for styles defined in styles.py."""
    font_px = int(st.session_state.get(f"lesson_font_{spec_id}", 22))
    marker = f"alora-a11y-{spec_id}"
    return (
        f'<div class="{marker}" style="--alora-font:{font_px}px;display:none;" '
        f'aria-hidden="true"></div>'
    )


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
        )

    st.markdown(_a11y_marker_html(spec_id), unsafe_allow_html=True)
    components.html(_reading_ruler_html(spec_id), height=0)


def get_workspace_layout_css() -> str:
    """Deprecated — layout CSS is in styles.get_custom_css()."""
    return ""
