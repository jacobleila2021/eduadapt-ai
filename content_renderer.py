"""
Render AI-generated lesson content with diagrams, colors, and rich HTML.
"""

import re
import uuid

import streamlit as st
import streamlit.components.v1 as components

_MERMAID_PATTERN = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def _render_mermaid(diagram: str, height: int = 420) -> None:
    """Render a Mermaid flowchart via CDN with explicit mermaid.run (Mermaid 10+)."""
    diagram_id = f"mermaid_{uuid.uuid4().hex[:8]}"
    safe = diagram.strip().replace("</", "<\\/").replace("`", "'")
    components.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
        <style>
          body {{ margin: 0; background: #fafcfd; }}
          #{diagram_id} {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            min-height: 120px;
            padding: 12px;
            box-sizing: border-box;
          }}
          .mermaid svg {{ margin: 0 auto; max-width: 100%; height: auto; }}
          .mermaid-fallback {{
            color: #0B2E59;
            font-family: Lexend, Arial, sans-serif;
            font-size: 14px;
            padding: 1rem;
            white-space: pre-wrap;
          }}
        </style>
        <pre class="mermaid" id="{diagram_id}">{safe}</pre>
        <script>
          (async function () {{
            mermaid.initialize({{
              startOnLoad: false,
              securityLevel: "loose",
              theme: "base",
              themeVariables: {{
                primaryColor: "#e6f7f8",
                primaryTextColor: "#0B2E59",
                primaryBorderColor: "#008C95",
                secondaryColor: "#e3f2fd",
                tertiaryColor: "#ecfdf5",
                lineColor: "#008C95",
                fontFamily: "Lexend, Arial, sans-serif",
                fontSize: "14px",
                nodeBorder: "#008C95",
                clusterBkg: "#f0f4f8",
                titleColor: "#0B2E59",
                edgeLabelBackground: "#ffffff"
              }},
              flowchart: {{
                htmlLabels: false,
                curve: "basis",
                padding: 16,
                useMaxWidth: true
              }}
            }});
            const el = document.getElementById("{diagram_id}");
            try {{
              await mermaid.run({{ nodes: [el] }});
            }} catch (err) {{
              el.outerHTML =
                '<div class="mermaid-fallback">Flowchart preview unavailable. '
                + 'Please regenerate adaptations or refresh the page.</div>';
              console.error("Mermaid render error:", err);
            }}
          }})();
        </script>
        """,
        height=height,
        scrolling=True,
    )


def render_rich_content(content: str) -> None:
    """
    Display markdown/HTML content and render embedded Mermaid diagram blocks.

    AI output may include:
    - HTML colored boxes and inline SVG study diagrams
    - ```mermaid code blocks for flowcharts
    - Standard markdown headings and lists
    """
    if not content or not content.strip():
        st.info("No content generated for this section.")
        return

    parts = _MERMAID_PATTERN.split(content)
    for index, part in enumerate(parts):
        if not part.strip():
            continue
        if index % 2 == 1:
            _render_mermaid(part)
        else:
            st.markdown(part, unsafe_allow_html=True)


def strip_mermaid_for_export(content: str) -> str:
    """Plain-text export: replace mermaid blocks with a readable placeholder."""
    def _replace(match: re.Match) -> str:
        body = match.group(1).strip()
        return f"\n[DIAGRAM — paste into mermaid.live to view]\n{body}\n"

    return _MERMAID_PATTERN.sub(_replace, content)
