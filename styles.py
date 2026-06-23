"""
Custom CSS for Alora AI — EduAdapt-style hero + readable main content.
"""

from config import (
    COLOR_DEEP_NAVY,
    COLOR_ELECTRIC_CYAN,
    COLOR_SILVER,
    COLOR_TEAL,
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
        max-width: 1100px;
    }}

    .main, .main p, .main li, .main span, .main label,
    .main .stMarkdown, .main h2, .main h3, .main h4 {{
        color: {COLOR_TEXT};
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(180deg, {COLOR_DEEP_NAVY} 0%, #0a2540 100%);
    }}

    section[data-testid="stSidebar"] .sidebar-spacer {{
        height: 5.5rem;
    }}

    section[data-testid="stSidebar"] .sidebar-tips-heading {{
        color: {COLOR_ELECTRIC_CYAN};
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin: 0 0 0.75rem 0;
    }}

    section[data-testid="stSidebar"] .sidebar-tip {{
        background: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(0, 140, 149, 0.45);
        border-left: 4px solid {COLOR_TEAL};
        border-radius: 10px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.85rem;
        color: {COLOR_WHITE};
        font-size: 0.88rem;
        line-height: 1.55;
    }}

    section[data-testid="stSidebar"] .sidebar-tip strong {{
        color: {COLOR_ELECTRIC_CYAN};
    }}

    section[data-testid="stSidebar"] .sidebar-tip-num {{
        display: inline-block;
        background: {COLOR_TEAL};
        color: {COLOR_WHITE};
        font-weight: 700;
        border-radius: 6px;
        padding: 0.12rem 0.5rem;
        margin-right: 0.35rem;
        font-size: 0.72rem;
    }}

    section[data-testid="stSidebar"] .sidebar-status-ready {{
        background: rgba(0, 140, 149, 0.2);
        border: 1px solid {COLOR_TEAL};
        border-radius: 10px;
        padding: 0.55rem 0.75rem;
        text-align: center;
        color: {COLOR_WHITE};
        font-weight: 600;
        font-size: 0.88rem;
    }}

    section[data-testid="stSidebar"] .sidebar-version {{
        color: {COLOR_SILVER};
        font-size: 0.78rem;
        text-align: center;
        margin-top: 1.5rem;
    }}

    /* ---- Hero banner (EduAdapt-style, centred) ---- */
    .alora-hero {{
        background: linear-gradient(135deg, {COLOR_DEEP_NAVY} 0%, {COLOR_TEAL} 100%);
        padding: 1.75rem 2rem 2rem;
        border-radius: 16px;
        text-align: center;
        color: {COLOR_WHITE};
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 28px rgba(4, 27, 77, 0.28);
    }}

    .alora-hero h1 {{
        margin: 0.75rem 0 0.35rem 0;
        font-size: 2.35rem;
        font-weight: 700;
        color: {COLOR_WHITE} !important;
        letter-spacing: -0.02em;
    }}

    .alora-hero .hero-tagline {{
        margin: 0;
        font-size: 1.15rem;
        color: {COLOR_SILVER};
        font-weight: 500;
    }}

    .alora-hero .hero-sub {{
        margin: 0.65rem 0 0 0;
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.88);
    }}

    /* ---- Metrics ---- */
    .metric-card {{
        background: {COLOR_WHITE};
        border-left: 4px solid {COLOR_TEAL};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 2px 12px rgba(11, 46, 89, 0.08);
        margin-bottom: 0.75rem;
    }}

    .metric-card h4 {{
        color: {COLOR_DEEP_NAVY};
        margin: 0 0 0.25rem 0;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .metric-card p {{
        color: {COLOR_TEAL};
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
    }}

    /* ---- Adaptation grid ---- */
    .adapt-nav-hint {{
        color: {COLOR_DEEP_NAVY};
        font-size: 0.92rem;
        margin: 0 0 0.85rem 0;
        padding: 0.65rem 1rem;
        background: #eef4f8;
        border-left: 4px solid {COLOR_TEAL};
        border-radius: 0 10px 10px 0;
    }}

    .adapt-nav-grid [data-testid="column"] button[kind="primary"] {{
        background: {COLOR_TEAL} !important;
        color: {COLOR_WHITE} !important;
        border: none !important;
        font-weight: 600;
        border-radius: 8px;
    }}

    .adapt-nav-grid [data-testid="column"] button[kind="secondary"] {{
        background: #eef4f8 !important;
        color: {COLOR_DEEP_NAVY} !important;
        border: 1px solid #c8d8e4 !important;
        font-weight: 500;
        border-radius: 8px;
    }}

    .adapt-nav-grid [data-testid="column"] button {{
        min-height: 2.85rem;
        white-space: normal;
        line-height: 1.25;
        font-size: 0.82rem;
    }}

    .main th {{
        background: {COLOR_DEEP_NAVY};
        color: {COLOR_WHITE};
    }}

    .main td {{
        border: 1px solid {COLOR_SILVER};
        color: {COLOR_TEXT};
    }}
    </style>
    """
