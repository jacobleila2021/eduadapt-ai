"""
Render AI-generated lesson content with diagrams, colors, and rich HTML.
"""

import re
import uuid

import streamlit as st
import streamlit.components.v1 as components

_MERMAID_PATTERN = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def _render_mermaid(diagram: str, height: int = 420) -> None:
    """Render a Mermaid diagram via CDN (flowcharts, concept maps)."""
    diagram_id = f"mermaid_{uuid.uuid4().hex[:8]}"
    # Avoid breaking out of the pre tag; mermaid syntax must stay unescaped.
    safe = diagram.strip().replace("</", "<\\/")
    components.html(
        f"""
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <pre class="mermaid" id="{diagram_id}">{safe}</pre>
        <script>
            mermaid.initialize({{
                startOnLoad: true,
                theme: "base",
                themeVariables: {{
                    primaryColor: "#e6f7f8",
                    primaryTextColor: "#0B2E59",
                    primaryBorderColor: "#008C95",
                    lineColor: "#008C95",
                    secondaryColor: "#f0f4f8",
                    tertiaryColor: "#fff"
                }}
            }});
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
