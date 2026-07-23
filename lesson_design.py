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
    .alora-ld-section {{
        transition: box-shadow 0.2s ease;
    }}
    .alora-ld-section:hover {{
        box-shadow: 0 8px 28px rgba(51,51,51,0.12) !important;
    }}
    #alora-ruler-bar {{
        transition: background 0.15s ease, opacity 0.15s ease, height 0.15s ease, width 0.15s ease;
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
        border-radius: 22px;
        padding: 1.5rem 1.35rem 1.6rem 1.35rem;
        min-height: 340px;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        gap: 0.65rem;
        box-sizing: border-box;
        position: relative;
        box-shadow: 0 10px 28px rgba(11, 46, 89, 0.08);
    }}
    .alora-vocab-number {{
        width: 2.4rem;
        height: 2.4rem;
        border-radius: 999px;
        background: {ACCENT_INTRO};
        color: #fff;
        font-weight: 800;
        font-size: 1.05rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: {FONT_STACK};
        margin-bottom: 0.15rem;
    }}
    .alora-vocab-icon {{
        font-size: 1.35rem;
        line-height: 1;
    }}
    .alora-word-wall-term {{
        color: {ACCENT_INFO};
        font-weight: 800;
        font-size: 1.85rem;
        line-height: 1.2;
        font-family: {FONT_STACK};
        margin: 0.35rem 0 0.45rem 0;
        letter-spacing: 0.01em;
        text-align: center;
    }}
    .lce-vocab-term {{
        color: {ACCENT_INFO};
        font-weight: 800;
        font-size: 1.9rem;
        line-height: 1.15;
        text-align: center;
        margin: 0.25rem 0 0.5rem 0;
        font-family: {FONT_STACK};
    }}
    .pqle-vocab-card {{
        background: linear-gradient(180deg, #ffffff 0%, {BG_MAIN} 100%);
        border: 1px solid {BORDER_SUBTLE};
        box-shadow: 0 14px 34px rgba(11, 46, 89, 0.09);
    }}
    .lce-vocab-body p, .alora-word-wall-body p {{
        margin: 0 0 0.45rem 0;
    }}
    .lce-vocab-tags .lce-tag, .alora-vocab-meta span {{
        font-size: 0.72rem;
        font-weight: 600;
        color: {ACCENT_INTRO};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 999px;
        padding: 0.15rem 0.55rem;
        margin-right: 0.25rem;
        display: inline-block;
    }}
    .alora-lesson-section {{
        margin: 1.35rem 0 1.6rem 0;
        padding: 0.15rem 0 0.35rem 0;
    }}
    .alora-lesson-prose {{
        font-size: 1.05rem;
        line-height: 1.75;
        letter-spacing: 0.015em;
        color: {TEXT_BODY};
        max-width: 46rem;
    }}
    .alora-vocab-meta {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.35rem;
        justify-content: center;
        margin-bottom: 0.35rem;
    }}
    .alora-vocab-meta span {{
        font-size: 0.75rem;
        font-weight: 600;
        color: {ACCENT_INTRO};
        border: 1px solid {BORDER_SUBTLE};
        border-radius: 999px;
        padding: 0.15rem 0.55rem;
        font-family: {FONT_STACK};
    }}
    .alora-word-wall-body {{
        color: {TEXT_BODY};
        font-weight: 500;
        font-size: 0.98rem;
        line-height: 1.7;
        letter-spacing: 0.02em;
        font-family: {FONT_STACK};
        width: 100%;
        text-align: left;
    }}
    .alora-vocab-def {{
        margin: 0 0 0.55rem 0;
        font-size: 1.02rem;
    }}
    .alora-vocab-simple, .alora-vocab-example, .alora-vocab-tip, .alora-vocab-ctx {{
        margin: 0 0 0.45rem 0;
    }}
    .alora-vocab-extras {{
        margin-top: 0.55rem;
        font-size: 0.86rem;
        color: {TEXT_BODY};
        opacity: 0.82;
        line-height: 1.55;
    }}
    .alora-word-wall-body strong {{
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


_LD_SECTION_THEMES = [
    ("#059669", "#ecfdf5", "🌟"),
    ("#1E3A8A", "#dbeafe", "💡"),
    ("#7c3aed", "#f3e8ff", "📌"),
    ("#c2410c", "#ffedd5", "🔍"),
    ("#0F766E", "#ccfbf1", "✨"),
    ("#db2777", "#fce7f3", "🎯"),
]


def _render_bold_markdown(text: str) -> str:
    """Convert **bold** markdown to HTML strong tags."""
    parts = re.split(r"\*\*(.+?)\*\*", text)
    out: list[str] = []
    for index, part in enumerate(parts):
        if index % 2 == 1:
            out.append(f"<strong>{html.escape(part)}</strong>")
        else:
            out.append(html.escape(part))
    return "".join(out)


def format_visual_practice_html(body: str) -> str:
    """Numbered Q on one line, numbered A on the next — for Visual Learner practice."""
    text = (body or "").strip()
    if not text:
        return ""

    lines = [ln.strip() for ln in re.split(r"\n+", text) if ln.strip()]
    q_re = re.compile(r"^(?:Q\s*)?(\d+)[.)]\s*(.+)$", re.I)
    a_re = re.compile(r"^(?:A(?:nswer)?\s*)?(\d+)[.)]\s*(.+)$", re.I)
    ans_plain = re.compile(r"^Answer\s*[:\-]\s*(.+)$", re.I)

    pairs: list[tuple[str, str, str]] = []
    pending_q: tuple[str, str] | None = None

    for line in lines:
        qm = q_re.match(line)
        am = a_re.match(line)
        if qm:
            if pending_q:
                pairs.append((pending_q[0], pending_q[1], ""))
            pending_q = (qm.group(1), qm.group(2))
        elif am:
            num = am.group(1)
            ans = am.group(2)
            if pending_q and pending_q[0] == num:
                pairs.append((num, pending_q[1], ans))
                pending_q = None
            else:
                pairs.append((num, pending_q[1] if pending_q else f"Question {num}", ans))
                pending_q = None
        elif pending_q and ans_plain.match(line):
            pairs.append((pending_q[0], pending_q[1], ans_plain.match(line).group(1)))
            pending_q = None
        elif pending_q:
            pairs.append((pending_q[0], pending_q[1], line))
            pending_q = None

    if pending_q:
        pairs.append((pending_q[0], pending_q[1], ""))

    if not pairs:
        return format_lesson_body_html(text, bullet_mode=False)

    blocks: list[str] = []
    for num, question, answer in pairs:
        blocks.append(
            f'<div class="alora-practice-pair" style="margin-bottom:1.35rem;padding:1rem 1.25rem;'
            f'background:#f8fafc;border-radius:12px;border-left:5px solid {ACCENT_INFO};">'
            f'<p style="font-weight:700;margin:0 0 0.65rem 0;line-height:1.7;">'
            f'<span style="color:{ACCENT_INFO};font-size:1.1rem;">Q{num}.</span> '
            f'{_render_bold_markdown(question)}</p>'
        )
        if answer:
            blocks.append(
                f'<p style="margin:0;padding-left:1.25rem;line-height:1.7;color:{TEXT_BODY};">'
                f'<span style="color:{ACCENT_INTRO};font-weight:700;">A{num}.</span> '
                f'{_render_bold_markdown(answer)}</p></div>'
            )
        else:
            blocks.append("</div>")

    return "\n".join(blocks)


def format_lesson_body_html(body: str, *, bullet_mode: bool = False, luxury_mode: bool = False) -> str:
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
            (
                f'<li style="margin-bottom:0.85rem;padding-left:0.25rem;line-height:1.85;">'
                f'<span style="color:{ACCENT_INTRO if luxury_mode else TEXT_BODY};'
                f'font-weight:700;margin-right:0.35rem;">{"▸" if luxury_mode else "•"}</span>'
                f'{_render_bold_markdown(item)}</li>'
            )
            for item in items
            if item
        )
        list_style = "none" if luxury_mode else "disc"
        padding = "0.25rem 0 0 0" if luxury_mode else "0 0 0 1.5rem"
        return (
            f'<ul class="alora-lesson-bullets" style="margin:0;padding:{padding};'
            f'list-style:{list_style};">{lis}</ul>'
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


def dyslexia_luxe_section_card_html(
    title: str, body: str, variant: str, index: int = 0
) -> str:
    """Rich coloured card for Dyslexia Smart — substantial layout with emoji and tint."""
    accent, bg_tint, emoji = _LD_SECTION_THEMES[index % len(_LD_SECTION_THEMES)]
    safe_title = html.escape(title)
    body_html = format_lesson_body_html(body, bullet_mode=True, luxury_mode=True)
    return f"""
    <div class="alora-ld-section alora-lesson-section" style="
        background: linear-gradient(145deg, {BG_MAIN} 0%, {bg_tint} 100%);
        border: 3px solid {accent};
        border-radius: 20px;
        padding: 32px 36px;
        margin: 1.5rem 0;
        box-shadow: 0 6px 20px rgba(51,51,51,0.1);
        text-align:left;
        font-family:{FONT_STACK};
        color:{TEXT_BODY};">
      <div style="display:flex;align-items:center;gap:0.85rem;margin-bottom:1.15rem;">
        <span style="font-size:2rem;line-height:1;" aria-hidden="true">{emoji}</span>
        <h3 style="color:{accent};font-weight:700;font-size:1.45rem;margin:0;
            font-family:{FONT_STACK};">{safe_title}</h3>
      </div>
      <div class="alora-lesson-body" style="font-size:1.08rem;color:{TEXT_BODY};max-width:52em;">
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
