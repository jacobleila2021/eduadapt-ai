"""
Accessibility tools — reading ruler, dyslexia-friendly text sizing.
CSS lives in styles.py; font size and ruler are applied via JS on the parent page.
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


def _a11y_sync_html(spec_id: str) -> str:
    """Apply font size + reading ruler on the parent Streamlit page (re-synced every rerun)."""
    font_px = int(st.session_state.get(f"lesson_font_{spec_id}", 18))
    show = st.session_state.get(f"show_ruler_{spec_id}", False)
    color_name = st.session_state.get(f"ruler_color_{spec_id}", "Soft Yellow")
    opacity = float(st.session_state.get(f"ruler_opacity_{spec_id}", 0.45))
    width = int(st.session_state.get(f"ruler_width_{spec_id}", 100))
    height = int(st.session_state.get(f"ruler_height_{spec_id}", 48))
    hex_color = RULER_COLORS.get(color_name, "#FFF59D")
    cfg = {
        "show": bool(show),
        "color": hex_color,
        "opacity": opacity,
        "width": width,
        "height": height,
        "fontPx": font_px,
    }

    return f"""
    <script>
    (function() {{
      const cfg = {json.dumps(cfg)};
      function topWin() {{
        try {{ return window.top || window.parent || window; }} catch (e) {{ return window; }}
      }}
      function pageDoc() {{
        const w = topWin();
        try {{
          if (w && w.document && w.document.body) return w.document;
        }} catch (e) {{}}
        return document;
      }}
      function mainRoot(d) {{
        return (
          d.querySelector('[data-testid="stMain"] .block-container') ||
          d.querySelector('.main .block-container') ||
          d.querySelector('.block-container') ||
          d.body
        );
      }}
      function syncAll() {{
        const w = topWin();
        const active = w.__aloraA11yCfg || cfg;
        const d = pageDoc();
        const root = mainRoot(d);
        if (root) {{
          root.style.setProperty("--alora-font", active.fontPx + "px");
        }}
        let bar = d.getElementById("alora-ruler-bar");
        if (!bar) {{
          bar = d.createElement("div");
          bar.id = "alora-ruler-bar";
          bar.setAttribute("aria-hidden", "true");
          d.body.appendChild(bar);
        }}
        bar.style.position = "fixed";
        bar.style.left = "50%";
        bar.style.transform = "translateX(-50%)";
        bar.style.pointerEvents = "none";
        bar.style.zIndex = "9999999";
        bar.style.borderRadius = "8px";
        bar.style.boxSizing = "border-box";
        bar.style.width = active.width + "%";
        bar.style.height = active.height + "px";
        bar.style.background = active.color;
        bar.style.opacity = String(active.opacity);
        bar.style.display = active.show ? "block" : "none";
        bar.dataset.aloraHeight = String(active.height);
      }}
      const w = topWin();
      w.__aloraA11yCfg = cfg;
      syncAll();
      if (!w.__aloraA11yPoll) {{
        w.__aloraA11yPoll = setInterval(syncAll, 350);
      }}
      const d = pageDoc();
      if (!d.__aloraRulerMoveBound) {{
        d.__aloraRulerMoveBound = true;
        d.addEventListener("mousemove", function(e) {{
          const tw = topWin();
          const active = tw.__aloraA11yCfg || {{}};
          const bar = d.getElementById("alora-ruler-bar");
          if (!bar || !active.show) return;
          const h = parseInt(bar.dataset.aloraHeight || "48", 10) || 48;
          bar.style.top = Math.max(0, e.clientY - h / 2) + "px";
        }}, true);
      }}
    }})();
    </script>
    """


def render_accessibility_toolbar(spec_id: str) -> None:
    """Reading ruler + font size controls."""
    with st.expander("📏 Reading Ruler & Text Size", expanded=False):
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
            16,
            32,
            18,
            key=f"lesson_font_{spec_id}",
        )

    components.html(_a11y_sync_html(spec_id), height=64, scrolling=False)


def get_workspace_layout_css() -> str:
    """Deprecated — layout CSS is in styles.get_custom_css()."""
    return ""
