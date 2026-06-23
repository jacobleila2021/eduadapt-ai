"""
Custom CSS for Alora AI — luxe, high-contrast, readable.
"""

from config import (
    COLOR_BRIGHT_AQUA,
    COLOR_DEEP_NAVY,
    COLOR_ELECTRIC_CYAN,
    COLOR_PAGE_BG,
    COLOR_TEXT,
    COLOR_WHITE,
)


def get_custom_css() -> str:
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .main .block-container {{
        padding-top: 1rem;
        max-width: 1180px;
        background: {COLOR_PAGE_BG};
    }}

    .main, .main p, .main li, .main span, .main label,
    .main .stMarkdown, .main h1, .main h2, .main h3, .main h4 {{
        color: {COLOR_TEXT};
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* ---- Sidebar: navy panel, scoped text (no global * override) ---- */
    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(180deg, {COLOR_DEEP_NAVY} 0%, #021a42 100%);
    }}

    section[data-testid="stSidebar"] .sidebar-tip {{
        background: rgba(20, 217, 229, 0.12);
        border: 1px solid rgba(20, 217, 229, 0.45);
        border-radius: 12px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.75rem;
        color: {COLOR_WHITE};
        font-size: 0.9rem;
        line-height: 1.5;
    }}

    section[data-testid="stSidebar"] .sidebar-tip strong {{
        color: {COLOR_BRIGHT_AQUA};
    }}

    section[data-testid="stSidebar"] .sidebar-tip-num {{
        display: inline-block;
        background: {COLOR_ELECTRIC_CYAN};
        color: {COLOR_DEEP_NAVY};
        font-weight: 700;
        border-radius: 6px;
        padding: 0.1rem 0.45rem;
        margin-right: 0.35rem;
        font-size: 0.75rem;
    }}

    section[data-testid="stSidebar"] .sidebar-status-ready {{
        background: rgba(20, 217, 229, 0.15);
        border: 1px solid {COLOR_ELECTRIC_CYAN};
        border-radius: 10px;
        padding: 0.55rem 0.75rem;
        text-align: center;
        color: {COLOR_BRIGHT_AQUA};
        font-weight: 600;
        font-size: 0.88rem;
        margin-bottom: 0.75rem;
    }}

    /* ---- Header ---- */
    .alora-header {{
        background: {COLOR_WHITE};
        border: 1px solid rgba(20, 217, 229, 0.35);
        border-radius: 14px;
        padding: 0.75rem 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 20px rgba(4, 27, 77, 0.06);
    }}

    .alora-title {{
        color: {COLOR_DEEP_NAVY};
        font-size: 1.65rem;
        font-weight: 700;
        margin: 0;
    }}

    .alora-tagline {{
        color: {COLOR_ELECTRIC_CYAN};
        font-size: 1rem;
        font-weight: 600;
        margin: 0.25rem 0 0 0;
    }}

    /* ---- Metrics ---- */
    .metric-card {{
        background: {COLOR_WHITE};
        border: 1px solid rgba(20, 217, 229, 0.35);
        border-left: 4px solid {COLOR_ELECTRIC_CYAN};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 2px 10px rgba(4, 27, 77, 0.06);
    }}

    .metric-card h4 {{
        color: {COLOR_DEEP_NAVY};
        margin: 0 0 0.25rem 0;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    .metric-card p {{
        color: {COLOR_ELECTRIC_CYAN};
        margin: 0;
        font-size: 1.45rem;
        font-weight: 700;
    }}

    /* ---- Adaptation tab grid ---- */
    .adapt-nav-hint {{
        color: {COLOR_DEEP_NAVY};
        font-size: 0.92rem;
        margin: 0 0 0.85rem 0;
        padding: 0.6rem 0.9rem;
        background: {COLOR_WHITE};
        border-left: 4px solid {COLOR_ELECTRIC_CYAN};
        border-radius: 0 8px 8px 0;
        border: 1px solid rgba(20, 217, 229, 0.25);
        border-left: 4px solid {COLOR_ELECTRIC_CYAN};
    }}

    .adapt-nav-grid [data-testid="column"] button[kind="primary"] {{
        background: {COLOR_DEEP_NAVY} !important;
        color: {COLOR_BRIGHT_AQUA} !important;
        border: 2px solid {COLOR_ELECTRIC_CYAN} !important;
        font-weight: 600;
        border-radius: 10px;
    }}

    .adapt-nav-grid [data-testid="column"] button[kind="secondary"] {{
        background: {COLOR_WHITE} !important;
        color: {COLOR_DEEP_NAVY} !important;
        border: 1px solid rgba(20, 217, 229, 0.45) !important;
        font-weight: 600;
        border-radius: 10px;
    }}

    .adapt-nav-grid [data-testid="column"] button {{
        min-height: 2.75rem;
        white-space: normal;
        line-height: 1.2;
        font-size: 0.8rem;
    }}

    /* ---- Lesson content area ---- */
    .main th {{
        background: {COLOR_DEEP_NAVY};
        color: {COLOR_WHITE};
    }}

    .main td {{
        background: {COLOR_WHITE};
        color: {COLOR_TEXT};
        border: 1px solid rgba(20, 217, 229, 0.3);
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: {COLOR_WHITE};
        border-color: rgba(20, 217, 229, 0.35) !important;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: {COLOR_WHITE};
        color: {COLOR_DEEP_NAVY};
        font-weight: 600;
        border: 1px solid rgba(20, 217, 229, 0.35);
        border-radius: 8px 8px 0 0;
    }}

    .stTabs [aria-selected="true"] {{
        background: {COLOR_DEEP_NAVY} !important;
        color: {COLOR_BRIGHT_AQUA} !important;
    }}
    </style>
    """
