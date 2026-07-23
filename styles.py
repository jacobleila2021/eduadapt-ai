"""
Premium CSS for Alora AI — top nav, sidebar, dashboard, pill tabs, workspace.
"""

from config import (
    COLOR_BRIGHT_AQUA,
    COLOR_DEEP_NAVY,
    COLOR_ELECTRIC_CYAN,
    COLOR_SILVER,
    COLOR_TEAL,
    COLOR_TEXT,
    COLOR_WHITE,
)
from lesson_design import get_workspace_css_fragment

# Luxury enterprise header (~35% taller than original 96px bar)
HEADER_HEIGHT_PX = 135


def get_custom_css() -> str:
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .main .block-container {{
        padding-top: 8.85rem;
        max-width: 1160px;
        padding-bottom: 2.5rem;
    }}

    .main, .main p, .main li, .main span, .main label,
    .main .stMarkdown, .main h2, .main h3, .main h4 {{
        color: {COLOR_TEXT};
    }}

    .main h2 {{
        font-weight: 700;
        letter-spacing: -0.02em;
        margin-bottom: 0.65rem;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{
        background: transparent;
        height: 0;
    }}

    .alora-skip-link {{
        position: fixed;
        top: 0.5rem;
        left: 0.75rem;
        z-index: 1000000;
        transform: translateY(-160%);
        background: {COLOR_WHITE};
        color: {COLOR_DEEP_NAVY};
        padding: 0.65rem 1rem;
        border: 2px solid {COLOR_ELECTRIC_CYAN};
        border-radius: 8px;
        font-weight: 700;
    }}
    .alora-skip-link:focus {{
        transform: translateY(0);
    }}

    /* ---- Premium brand signage bar ---- */
    .alora-topnav {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999999;
        background: linear-gradient(180deg, #051a42 0%, {COLOR_DEEP_NAVY} 50%, #031638 100%);
        box-shadow: 0 8px 36px rgba(4, 27, 77, 0.5);
        height: {HEADER_HEIGHT_PX}px;
    }}

    .topnav-accent {{
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, {COLOR_ELECTRIC_CYAN}, {COLOR_BRIGHT_AQUA}, {COLOR_ELECTRIC_CYAN});
    }}

    .topnav-inner {{
        display: grid;
        grid-template-columns: minmax(160px, 1fr) auto minmax(160px, 1fr);
        align-items: center;
        max-width: 1320px;
        margin: 0 auto;
        padding: 0 2rem 0 2.25rem;
        height: {HEADER_HEIGHT_PX}px;
    }}

    /* Logo — direct on header, no box or frame */
    .topnav-logo {{
        justify-self: start;
        display: flex;
        align-items: center;
        height: 100%;
        background: none !important;
        border: none !important;
        padding: 0 !important;
        box-shadow: none !important;
    }}

    .topnav-logo-img {{
        height: 108px;
        width: auto;
        max-width: none;
        object-fit: contain;
        display: block;
        margin-left: 0.25rem;
        filter: drop-shadow(0 4px 16px rgba(20, 217, 229, 0.45));
    }}

    .topnav-center {{
        justify-self: center;
        text-align: center;
        padding: 0.65rem 0;
    }}

    .topnav-title {{
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        white-space: nowrap;
        line-height: 1.1;
    }}

    .topnav-title .name-alora {{
        color: {COLOR_WHITE};
    }}

    .topnav-title .name-ai {{
        color: {COLOR_ELECTRIC_CYAN};
    }}

    .topnav-tagline {{
        color: rgba(255, 255, 255, 0.88);
        font-size: 0.92rem;
        font-weight: 500;
        letter-spacing: 0.03em;
        margin-top: 0.35rem;
        line-height: 1.4;
    }}

    .topnav-right {{
        justify-self: end;
        text-align: right;
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
    }}

    .topnav-address {{
        color: {COLOR_ELECTRIC_CYAN};
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}

    .topnav-url {{
        color: rgba(255, 255, 255, 0.78);
        font-size: 0.76rem;
        font-weight: 500;
    }}

    .topnav-version {{
        display: inline-block;
        margin-top: 0.35rem;
        padding: 0.2rem 0.65rem;
        background: rgba(20, 217, 229, 0.2);
        border: 1px solid rgba(20, 217, 229, 0.55);
        border-radius: 999px;
        color: {COLOR_BRIGHT_AQUA};
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.04em;
    }}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(180deg, {COLOR_DEEP_NAVY} 0%, #051633 100%);
        padding-top: 7.85rem;
    }}

    section[data-testid="stSidebar"] .sidebar-block {{
        margin-bottom: 1.35rem;
        padding: 0 0.15rem;
    }}

    section[data-testid="stSidebar"] .sidebar-block-title {{
        color: {COLOR_ELECTRIC_CYAN};
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0 0 0.65rem 0;
    }}

    section[data-testid="stSidebar"] .sidebar-item {{
        color: rgba(255, 255, 255, 0.92);
        font-size: 0.86rem;
        line-height: 1.55;
        padding: 0.4rem 0 0.4rem 1.5rem;
        position: relative;
    }}

    section[data-testid="stSidebar"] .sidebar-item::before {{
        content: "✓";
        position: absolute;
        left: 0;
        color: {COLOR_BRIGHT_AQUA};
        font-weight: 700;
        font-size: 0.75rem;
    }}

    section[data-testid="stSidebar"] .sidebar-divider {{
        border: none;
        border-top: 1px solid rgba(20, 217, 229, 0.2);
        margin: 1.25rem 0;
    }}

    section[data-testid="stSidebar"] .sidebar-status-ready {{
        background: rgba(20, 217, 229, 0.12);
        border: 1px solid rgba(20, 217, 229, 0.45);
        border-radius: 10px;
        padding: 0.55rem 0.75rem;
        text-align: center;
        color: {COLOR_WHITE};
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }}

    section[data-testid="stSidebar"] .sidebar-status-warn {{
        background: rgba(255, 193, 7, 0.12);
        border: 1px solid rgba(255, 193, 7, 0.45);
        border-radius: 10px;
        padding: 0.55rem 0.75rem;
        text-align: center;
        color: {COLOR_WHITE};
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }}

    section[data-testid="stSidebar"] .sidebar-meta {{
        color: {COLOR_SILVER};
        font-size: 0.78rem;
        text-align: center;
        line-height: 1.6;
        margin-top: 1.25rem;
    }}

    section[data-testid="stSidebar"] .sidebar-creator {{
        margin-top: 1rem;
        padding: 1rem 0.85rem;
        text-align: center;
        background: rgba(20, 217, 229, 0.12);
        border: 1px solid rgba(20, 217, 229, 0.45);
        border-radius: 12px;
    }}

    section[data-testid="stSidebar"] .sidebar-creator-label {{
        display: block;
        color: {COLOR_ELECTRIC_CYAN};
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 0.35rem;
    }}

    section[data-testid="stSidebar"] .sidebar-creator-name {{
        display: block;
        color: {COLOR_WHITE};
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }}

    /* ---- Dashboard ---- */
    .dashboard-hero {{
        background: linear-gradient(135deg, {COLOR_DEEP_NAVY} 0%, #0a3d5c 100%);
        border-radius: 18px;
        padding: 1.75rem 2.25rem;
        color: {COLOR_WHITE};
        margin-bottom: 1.75rem;
        box-shadow: 0 10px 40px rgba(4, 27, 77, 0.2);
    }}

    .dashboard-hero h2 {{
        color: {COLOR_WHITE} !important;
        margin: 0 0 0.5rem 0;
        font-size: 1.65rem;
    }}

    .dashboard-hero p {{
        color: rgba(255,255,255,0.9);
        margin: 0;
        font-size: 1rem;
        line-height: 1.5;
    }}

    .workspace-card {{
        background: {COLOR_WHITE};
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        box-shadow: 0 4px 24px rgba(4, 27, 77, 0.07);
        border: 1px solid rgba(4, 27, 77, 0.07);
        margin-bottom: 1.35rem;
    }}

    .adaptation-panel {{
        border-top: 4px solid {COLOR_ELECTRIC_CYAN};
        margin-top: 0.5rem;
    }}

    .multimodal-strip {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        margin: 1.15rem 0 0 0;
    }}

    .multimodal-chip {{
        background: rgba(20, 217, 229, 0.18);
        border: 1px solid rgba(20, 217, 229, 0.45);
        color: {COLOR_BRIGHT_AQUA};
        border-radius: 999px;
        padding: 0.4rem 0.95rem;
        font-size: 0.82rem;
        font-weight: 600;
    }}

    .metric-card {{
        background: #f8fcfd;
        border-left: 4px solid {COLOR_ELECTRIC_CYAN};
        border-radius: 12px;
        padding: 1.1rem 1.35rem;
        box-shadow: 0 2px 12px rgba(4, 27, 77, 0.05);
        margin-bottom: 0.5rem;
    }}

    .metric-card h4 {{
        color: {COLOR_DEEP_NAVY};
        margin: 0 0 0.3rem 0;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}

    .metric-card p {{
        color: {COLOR_TEAL};
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
    }}

    /* ---- Cyan pill tabs (Streamlit st-key-* selectors — CSS must NOT rely on wrapper divs) ---- */
    .pill-nav-hint {{
        color: #3d5470;
        font-size: 0.95rem;
        margin: 0 0 1.25rem 0;
        line-height: 1.5;
        font-weight: 500;
    }}

    div[class*="st-key-pill_"] button,
    div[class*="st-key-ws_pill_"] button,
    div[class*="st-key-subpill_"] button {{
        background: linear-gradient(180deg, #089aa4 0%, #066d75 100%) !important;
        color: {COLOR_WHITE} !important;
        border: 2px solid rgba(255, 255, 255, 0.55) !important;
        border-radius: 999px !important;
        min-height: 3.5rem !important;
        font-size: 1.08rem !important;
        font-weight: 700 !important;
        transition: all 0.22s ease !important;
        letter-spacing: 0.025em;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.35);
        box-shadow: 0 4px 16px rgba(4, 27, 77, 0.35);
    }}

    div[class*="st-key-pill_"] button:hover,
    div[class*="st-key-ws_pill_"] button:hover,
    div[class*="st-key-subpill_"] button:hover {{
        background: linear-gradient(180deg, #0ab0bd 0%, #087682 100%) !important;
        color: {COLOR_WHITE} !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 22px rgba(4, 27, 77, 0.45);
        border-color: {COLOR_WHITE} !important;
    }}

    div[class*="st-key-pill_"] button[kind="primary"],
    div[class*="st-key-ws_pill_"] button[kind="primary"],
    div[class*="st-key-subpill_"] button[kind="primary"],
    div[class*="st-key-pill_"] button[data-testid="baseButton-primary"],
    div[class*="st-key-ws_pill_"] button[data-testid="baseButton-primary"],
    div[class*="st-key-subpill_"] button[data-testid="baseButton-primary"] {{
        background: linear-gradient(180deg, {COLOR_DEEP_NAVY} 0%, #062456 100%) !important;
        color: {COLOR_WHITE} !important;
        border: 2px solid {COLOR_ELECTRIC_CYAN} !important;
        box-shadow: 0 0 14px rgba(20, 217, 229, 0.45), 0 4px 14px rgba(4, 27, 77, 0.35) !important;
    }}

    div[class*="st-key-pill_"] button[kind="secondary"],
    div[class*="st-key-ws_pill_"] button[kind="secondary"],
    div[class*="st-key-subpill_"] button[kind="secondary"],
    div[class*="st-key-pill_"] button[data-testid="baseButton-secondary"],
    div[class*="st-key-ws_pill_"] button[data-testid="baseButton-secondary"],
    div[class*="st-key-subpill_"] button[data-testid="baseButton-secondary"] {{
        background: linear-gradient(180deg, #089aa4 0%, #066d75 100%) !important;
        color: {COLOR_WHITE} !important;
        border: 2px solid rgba(255, 255, 255, 0.55) !important;
        box-shadow: 0 4px 16px rgba(4, 27, 77, 0.35) !important;
    }}

    .lesson-jump-nav {{
        display: none;
    }}

    .exam-print-header p {{
        font-size: 1.1rem;
        margin: 0.55rem 0;
        color: #333333;
        font-weight: 600;
    }}

    .exam-answer-reveal {{
        background: #FFF9C4;
        color: #059669;
        font-weight: 600;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        border: 1px solid #FDE68A;
        margin: 0.35rem 0 0.75rem 0;
        line-height: 1.65;
        white-space: pre-wrap;
    }}

    /* Fallback if st-key classes differ on Cloud */
    .main [data-testid="stHorizontalBlock"] .stButton button {{
        border-radius: 999px !important;
    }}

    div[class*="st-key-subpill_"] button {{
        min-height: 2.85rem !important;
        font-size: 0.92rem !important;
    }}

    .alora-picture-words-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1.25rem;
        margin: 1rem 0 1.5rem 0;
    }}

    @media (max-width: 900px) {{
        .alora-picture-words-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
    }}

    @media (max-width: 560px) {{
        .alora-picture-words-grid {{
            grid-template-columns: 1fr;
        }}
    }}

    .alora-picture-word-card {{
        background: #F7FAFC;
        border: 1px solid #e8dcc8;
        border-radius: 16px;
        padding: 0.85rem;
        text-align: center;
        box-sizing: border-box;
    }}

    .alora-picture-word-img {{
        width: 100%;
        height: auto;
        max-height: 220px;
        object-fit: contain;
        border-radius: 12px;
        background: #ffffff;
        display: block;
        margin: 0 auto 0.65rem auto;
    }}

    .alora-picture-word-term {{
        color: {COLOR_DEEP_NAVY};
        font-weight: 700;
        font-size: 1.05rem;
        margin: 0;
    }}

    .alora-picture-word-fallback {{
        min-height: 160px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #ffffff;
        border-radius: 12px;
        margin-bottom: 0.65rem;
        padding: 0.75rem;
        color: #4a6080;
        font-size: 0.92rem;
    }}

    .alora-picture-word-emoji {{
        font-size: 2rem;
        margin-bottom: 0.35rem;
    }}

    .alora-study-diagram {{
        width: 100%;
        margin: 1rem 0 1.75rem;
        padding: 1rem;
        border-radius: 24px;
        background:
            radial-gradient(circle at 10% 10%, rgba(34, 211, 238, 0.10), transparent 32%),
            linear-gradient(145deg, #ffffff 0%, #f5fbff 100%);
        border: 1px solid rgba(6, 182, 212, 0.20);
        box-shadow: 0 18px 46px rgba(4, 27, 77, 0.12);
        box-sizing: border-box;
    }}

    .alora-study-diagram svg {{
        max-width: 100%;
        height: auto;
        border-radius: 18px;
        display: block;
    }}

    .viewer-header {{
        background: linear-gradient(135deg, #eef9fb 0%, #f8fbfd 100%);
        border-radius: 14px;
        padding: 1.35rem 1.65rem;
        margin-bottom: 1.25rem;
        border-left: 5px solid {COLOR_ELECTRIC_CYAN};
    }}

    .workspace-banner {{
        background: linear-gradient(135deg, {COLOR_DEEP_NAVY} 0%, #0a3d6e 100%);
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        margin-bottom: 1.25rem;
        color: {COLOR_WHITE};
        box-shadow: 0 8px 28px rgba(4, 27, 77, 0.25);
    }}

    .workspace-mode-strip {{
        background: linear-gradient(90deg, #066d75, #089aa4);
        color: {COLOR_WHITE};
        font-weight: 700;
        font-size: 0.92rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        text-align: center;
        padding: 0.55rem 1rem;
        border-radius: 999px;
        margin: 0.75rem 0 1.25rem 0;
        box-shadow: 0 4px 14px rgba(4, 27, 77, 0.25);
    }}

    .bottom-tabs-label {{
        color: #334155;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin: 2rem 0 0.5rem 0;
        text-align: center;
    }}

    .main .block-container:has(.alora-workspace-active)
    [data-testid="stMarkdownContainer"]:has(.bottom-tabs-label) {{
        position: fixed !important;
        bottom: 13.25rem !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999992 !important;
        margin: 0 !important;
        padding: 0 !important;
        pointer-events: none;
    }}

    .main .block-container:has(.alora-workspace-active) .bottom-tabs-label {{
        color: rgba(255, 255, 255, 0.88) !important;
        margin: 0 !important;
    }}

    .main .block-container:has(.alora-workspace-active)
    [data-testid="stHorizontalBlock"]:has([class*="st-key-subpill_"]) {{
        position: fixed !important;
        bottom: 9.5rem !important;
        left: 0 !important;
        right: 0 !important;
        z-index: 999991 !important;
        background: linear-gradient(180deg, #041B4D, #031638) !important;
        padding: 0.35rem 1.5rem 0.5rem 1.5rem !important;
        margin: 0 !important;
        max-width: 100vw !important;
    }}

    .workspace-banner h2 {{
        color: {COLOR_WHITE} !important;
        margin: 0 0 0.35rem 0;
    }}

    .workspace-banner p {{
        color: rgba(255,255,255,0.88);
        margin: 0;
        font-size: 0.95rem;
    }}

    .stDownloadButton button {{
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
        border: 1px solid rgba(20, 217, 229, 0.35) !important;
    }}

    .stDownloadButton button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 14px rgba(20, 217, 229, 0.35);
    }}

    .viewer-header h2 {{
        margin: 0 0 0.35rem 0;
        color: {COLOR_DEEP_NAVY} !important;
    }}

    .viewer-header p {{
        margin: 0;
        color: #4a6080;
        font-size: 0.92rem;
    }}

    .main th {{
        background: {COLOR_DEEP_NAVY};
        color: {COLOR_WHITE};
    }}

    .main td {{
        border: 1px solid {COLOR_SILVER};
        color: {COLOR_TEXT};
    }}

    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] small {{
        color: #51545d !important;
    }}

    :where(button, a, input, textarea, select, [tabindex]):focus-visible {{
        outline: 3px solid {COLOR_ELECTRIC_CYAN} !important;
        outline-offset: 3px !important;
    }}

    @media (prefers-reduced-motion: reduce) {{
        *, *::before, *::after {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
        }}
    }}

    @media (forced-colors: active) {{
        :where(button, a, input, textarea, select, [tabindex]) {{
            forced-color-adjust: auto;
        }}
        .alora-topnav, .workspace-card, .viewer-header, .alora-study-diagram {{
            border: 1px solid CanvasText !important;
        }}
    }}

    @media (max-width: 768px) {{
        .alora-topnav, .topnav-inner {{ height: 100px; }}
        .topnav-title {{ font-size: 1.5rem; }}
        .topnav-logo-img {{ height: 72px; }}
        .topnav-tagline, .topnav-right {{ display: none; }}
        .main .block-container {{ padding-top: 6.75rem; }}
        .main .block-container:has(.alora-workspace-active) {{
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            padding-bottom: 14rem !important;
        }}
    }}

    /* Dyslexia-friendly workspace (injected once — never via st.markdown) */
    {get_workspace_css_fragment()}
    </style>
    """
