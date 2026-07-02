"""
Dyslexia-friendly lesson screen design system — shared tokens and CSS.
"""

from __future__ import annotations

import html
import re

# ---- Palette ----
BG_MAIN = "#FFF9EE"
TEXT_BODY = "#333333"
BORDER_SUBTLE = "#E8E0CF"
SOFT_YELLOW = "#FFF59D"

ACCENT_INTRO = "#059669"  # Emerald Green — Introduction
ACCENT_INFO = "#1E3A8A"  # Dark Royal Blue — Information / Learn
ACCENT_STORY = "#C2410C"  # Burnt Sienna — Stories / Creativity

FONT_STACK = (
    '"OpenDyslexic", "Atkinson Hyperlegible", "Lexend", Verdana, sans-serif'
)

FONT_IMPORTS = """
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Lexend:wght@400;600;700&display=swap');
@font-face {
  font-family: 'OpenDyslexic';
  src: url('https://cdn.jsdelivr.net/npm/opendyslexic@1.0.3/dist/opendyslexic-regular.otf') format('opentype');
  font-weight: normal;
  font-style: normal;
  font-display: swap;
}
"""

_INTRO_KEYS = ("intro", "welcome", "hook", "overview", "start", "today", "warm")
_INFO_KEYS = (
    "learn", "explain", "concept", "information", "understand",
    "practice", "example", "key", "step", "review", "check", "mastery",
)
_STORY_KEYS = ("story", "creative", "imagine", "activity", "wonder", "explore", "think")


def classify_section(title: str, box: str, index: int) -> str:
    """Map a lesson section to introduction | information | stories."""
    t = (title or "").lower()
    b = (box or "").lower()
    if index == 0 or b == "intro" or any(k in t for k in _INTRO_KEYS):
        return "introduction"
    if b in ("orange",) or any(k in t for k in _STORY_KEYS):
        return "stories"
    if any(k in t for k in _INFO_KEYS) or b in ("teal", "blue", "green", "practice", "check"):
        return "information"
    return "information"


def accent_for_variant(variant: str) -> str:
    return {
        "introduction": ACCENT_INTRO,
        "information": ACCENT_INFO,
        "stories": ACCENT_STORY,
    }.get(variant, ACCENT_INFO)


def get_global_dyslexia_css() -> str:
    """Deprecated — styles are injected via styles.get_custom_css(). Returns marker only."""
    return ""


def get_workspace_css_fragment() -> str:
    """Raw CSS (no <style> tags) for inclusion in styles.get_custom_css()."""
    return f"""
    {FONT_IMPORTS}
    .main .block-container:has(.alora-workspace-active) {{
        background: {BG_MAIN} !important;
        padding-bottom: 320px !important;
    }}
    .main .block-container:has(.alora-workspace-active) [data-testid="stMarkdownContainer"] p,
    .main .block-container:has(.alora-workspace-active) [data-testid="stMarkdownContainer"] li,
    .main .block-container:has(.alora-workspace-active) [data-testid="stMarkdownContainer"] span,
    .main .block-container:has(.alora-workspace-active) [data-testid="stMarkdownContainer"] td,
    .main .block-container:has(.alora-workspace-active) [data-testid="stMarkdownContainer"] h1,
    .main .block-container:has(.alora-workspace-active) [data-testid="stMarkdownContainer"] h2,
    .main .block-container:has(.alora-workspace-active) [data-testid="stMarkdownContainer"] h3,
    .main .block-container:has(.alora-workspace-active) [data-testid="stMarkdownContainer"] h4,
    .main .block-container:has(.alora-workspace-active) [data-testid="stTextArea"] textarea,
    .main .block-container:has(.alora-workspace-active) [data-testid="stTextInput"] input,
    .main .block-container:has([class*="alora-a11y-"]) [data-testid="stMarkdownContainer"] p,
    .main .block-container:has([class*="alora-a11y-"]) [data-testid="stMarkdownContainer"] li,
    .main .block-container:has([class*="alora-a11y-"]) [data-testid="stMarkdownContainer"] span,
    .main .block-container:has([class*="alora-a11y-"]) .stAlert p,
    .main .block-container:has([class*="alora-a11y-"]) [data-testid="stTextArea"] textarea,
    .main .block-container:has([class*="alora-a11y-"]) [data-testid="stTextInput"] input {{
        font-family: {FONT_STACK} !important;
        color: {TEXT_BODY} !important;
        text-align: left !important;
        line-height: 1.75 !important;
        letter-spacing: 0.03em !important;
        font-size: var(--alora-font, 18px) !important;
        font-weight: var(--alora-weight, 400) !important;
    }}
    .main .block-container:has(.alora-auditory-active) .alora-lesson-section,
    .main .block-container:has(.alora-auditory-active) .alora-lesson-body,
    .main .block-container:has(.alora-auditory-active) .alora-lesson-bullets li {{
        font-size: 28px !important;
        font-weight: 700 !important;
        line-height: 2 !important;
        letter-spacing: 0.05em !important;
    }}
    .main .block-container:has(.alora-auditory-active) .alora-lesson-section h3 {{
        font-size: 1.5rem !important;
    }}
    .main .block-container:has(.alora-workspace-active) h2,
    .main .block-container:has(.alora-workspace-active) h3,
    .main .block-container:has(.alora-workspace-active) h4 {{
        font-weight: 700 !important;
    }}
    .main .block-container:has(.alora-workspace-active) [data-testid="stVerticalBlockBorderWrapper"] {{
        background: {BG_MAIN} !important;
        border-radius: 16px !important;
    }}
    .main .block-container:has(.alora-workspace-active)
    [data-testid="stHorizontalBlock"]:has([class*="st-key-ws_pill_"]) {{
        position: fixed !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999991 !important;
        background: linear-gradient(180deg, #041B4D, #031638) !important;
        padding: 0.35rem 1.5rem !important;
        margin: 0 !important;
        box-shadow: 0 -4px 18px rgba(0,0,0,0.28) !important;
        max-width: 100vw !important;
        width: 100% !important;
    }}
    .main .block-container:has(.alora-workspace-active)
    [data-testid="stHorizontalBlock"]:has([class*="st-key-ws_pill_"]):nth-last-of-type(1) {{
        bottom: 0 !important;
        padding-bottom: 1rem !important;
        box-shadow: 0 -8px 28px rgba(0,0,0,0.35) !important;
    }}
    .main .block-container:has(.alora-workspace-active)
    [data-testid="stHorizontalBlock"]:has([class*="st-key-ws_pill_"]):nth-last-of-type(2) {{
        bottom: 4.35rem !important;
    }}
    .main .block-container:has(.alora-workspace-active)
    [data-testid="stHorizontalBlock"]:has([class*="st-key-ws_pill_"]):nth-last-of-type(3) {{
        bottom: 8.7rem !important;
    }}
    .main .block-container:has(.alora-workspace-active) .alora-lesson-title p,
    .main .block-container:has(.alora-workspace-active) .alora-lesson-subtitle {{
        color: {SOFT_YELLOW} !important;
        opacity: 1 !important;
        font-weight: 600 !important;
    }}
    .alora-word-wall {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 1.25rem;
        margin: 1rem 0 1.5rem 0;
    }}
    @media (max-width: 768px) {{
        .alora-word-wall {{
            grid-template-columns: 1fr;
        }}
    }}
    .alora-word-wall-card {{
        background: {BG_MAIN};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 18px;
        padding: 1.35rem 1.5rem 1.5rem 1.5rem;
        min-height: 320px;
        display: flex;
        flex-direction: column;
        gap: 0.85rem;
        box-sizing: border-box;
    }}
    .alora-word-wall-term {{
        color: {TEXT_BODY};
        font-weight: 700;
        font-size: 1.2rem;
        line-height: 1.45;
        font-family: {FONT_STACK};
        margin: 0;
    }}
    .alora-word-wall-body {{
        color: {TEXT_BODY};
        font-weight: 500;
        font-size: 1rem;
        line-height: 1.85;
        letter-spacing: 0.03em;
        font-family: {FONT_STACK};
        flex: 1;
    }}
    .alora-word-wall-body strong {{
        color: {TEXT_BODY};
        font-weight: 700;
    }}
    .alora-word-wall-emoji {{
        font-size: 2rem;
        line-height: 1;
        margin: 0.15rem 0 0.35rem 0;
    }}
    .main .block-container:has(.alora-workspace-active)
    div[data-testid="element-container"]:has(.alora-audio-stick),
    .main .block-container:has(.alora-workspace-active)
    div[data-testid="element-container"]:has(.alora-audio-sticky-start) {{
        position: sticky !important;
        top: 8.5rem !important;
        z-index: 998 !important;
        background: {BG_MAIN} !important;
        padding-top: 0.15rem !important;
        padding-bottom: 0.15rem !important;
        border-bottom: 1px solid {BORDER_SUBTLE} !important;
    }}
    """


def format_lesson_body_html(body: str, *, bullet_mode: bool = False) -> str:
    """Plain-text lesson body as paragraphs or bullet list (ld / auditory)."""
    text = (body or "").strip()
    if not text:
        return ""

    if bullet_mode:
        items: list[str] = []
        for line in re.split(r"\n+", text):
            line = line.strip()
            if not line:
                continue
            if line.startswith(("- ", "* ", "• ")):
                items.append(line[2:].strip())
            elif re.match(r"^\d+[.)]\s+", line):
                items.append(re.sub(r"^\d+[.)]\s+", "", line).strip())
            else:
                items.append(line)
        if len(items) <= 1:
            plain = re.sub(r"\s+", " ", text)
            items = [
                s.strip()
                for s in re.split(r"(?<=[.!?])\s+", plain)
                if len(s.strip()) > 6
            ][:8]
        lis = "".join(
            f'<li style="margin-bottom:0.75rem;">{html.escape(item)}</li>'
            for item in items
            if item
        )
        return (
            f'<ul class="alora-lesson-bullets" style="margin:0;padding-left:1.5rem;'
            f'list-style:disc;">{lis}</ul>'
        )

    safe_body = html.escape(text)
    safe_body = re.sub(r"\n\n+", "</p><p>", safe_body)
    safe_body = safe_body.replace("\n", "<br/>")
    return f'<p style="margin:0 0 1rem 0;">{safe_body}</p>'


def section_card_html(title: str, body: str, variant: str, *, bullet_mode: bool = False) -> str:
    """Themed lesson section card — cream background, coloured accent border."""
    accent = accent_for_variant(variant)
    safe_title = html.escape(title)
    body_html = format_lesson_body_html(body, bullet_mode=bullet_mode)
    return f"""
    <div class="alora-lesson-section" style="
        background:{BG_MAIN};
        border:6px solid {accent};
        border-radius:16px;
        padding:28px 32px;
        margin:1.25rem 0;
        box-shadow:0 2px 8px rgba(51,51,51,0.06);
        text-align:left;
        font-family:{FONT_STACK};
        color:{TEXT_BODY};
        line-height:1.75;
        letter-spacing:0.03em;">
      <h3 style="color:{accent};font-weight:700;font-size:1.35rem;margin:0 0 1rem 0;
          font-family:{FONT_STACK};">{safe_title}</h3>
      <div class="alora-lesson-body" style="font-size:1.05rem;color:{TEXT_BODY};max-width:48em;">
        {body_html}
      </div>
    </div>
    """


def lesson_title_html(title: str, subtitle: str = "", variant: str = "introduction") -> str:
    accent = accent_for_variant(variant)
    sub = (
        f'<p class="alora-lesson-subtitle" style="color:{SOFT_YELLOW};font-size:1.1rem;'
        f'margin:0.5rem 0 0 0;font-family:{FONT_STACK};line-height:1.7;font-weight:600;">'
        f'{html.escape(subtitle)}</p>'
        if subtitle
        else ""
    )
    return f"""
    <div class="alora-lesson-title" style="margin:0 0 1.5rem 0;text-align:left;font-family:{FONT_STACK};">
      <h2 style="color:{accent};font-weight:700;font-size:1.9rem;margin:0;
          font-family:{FONT_STACK};">{html.escape(title)}</h2>
      {sub}
    </div>
    """


def get_audio_passage_css(font_px: int = 18, *, auditory_mode: bool = False) -> str:
    """Reading passage styling — identical across every lesson type."""
    if auditory_mode:
        font_px = 30
        weight = 700
        line_h = 2.0
    else:
        weight = 400
        line_h = 1.75
    return f"""
    {FONT_IMPORTS}
    .alora-audio-root {{
        font-family: {FONT_STACK};
        color: {TEXT_BODY};
        max-width: 48em;
    }}
    .alora-transcript-card {{
        background: {BG_MAIN};
        color: {TEXT_BODY};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 16px;
        padding: 28px 32px;
        line-height: {line_h};
        font-size: {font_px}px;
        font-weight: {weight};
        letter-spacing: 0.03em;
        min-height: 120px;
        text-align: left;
        margin-bottom: 1rem;
        box-shadow: none;
    }}
    .alora-transcript-card .speech-sentence {{
        margin: 0.65rem 0;
        padding: 0.35rem 0;
        color: {TEXT_BODY};
        transition: background 0.2s;
    }}
    .alora-transcript-card .speech-sentence.active {{
        background: rgba(232, 224, 207, 0.55);
        box-shadow: inset 4px 0 0 {ACCENT_INTRO};
        font-weight: 600;
        padding-left: 0.5rem;
        border-radius: 4px;
    }}
    .alora-audio-toolbar {{
        position: sticky;
        top: 0;
        z-index: 1000;
        background: {BG_MAIN};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 16px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.85rem;
        box-shadow: 0 2px 8px rgba(51,51,51,0.06);
    }}
    .alora-audio-controls, .alora-audio-settings {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        align-items: center;
    }}
    .alora-audio-settings {{ margin-top: 0.55rem; font-size: 1rem; color: {TEXT_BODY}; }}
    .alora-audio-root button {{
        background: {ACCENT_INFO};
        color: #fff;
        border: none;
        border-radius: 12px;
        padding: 0.65rem 1.25rem;
        min-height: 44px;
        min-width: 44px;
        font-weight: 700;
        cursor: pointer;
        font-size: 0.95rem;
        font-family: {FONT_STACK};
    }}
    .alora-audio-root button:hover {{ background: #172554; }}
    .alora-audio-root select {{
        background: {BG_MAIN};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 12px;
        padding: 0.5rem 0.65rem;
        min-height: 44px;
        margin-left: 0.35rem;
        color: {TEXT_BODY};
        font-family: {FONT_STACK};
        font-size: 0.95rem;
    }}
    .alora-stop-dialog {{
        margin-top: 0.75rem;
        padding: 1rem 1.25rem;
        background: {BG_MAIN};
        border: 2px solid {BORDER_SUBTLE};
        border-radius: 16px;
        color: {TEXT_BODY};
        font-family: {FONT_STACK};
    }}
    .alora-stop-dialog button {{
        background: {ACCENT_INTRO};
    }}
    """
