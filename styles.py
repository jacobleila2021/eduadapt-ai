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


def get_custom_css() -> str:
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }}

    .main .block-container {{
        padding-top: 4.5rem;
        max-width: 1140px;
    }}

    .main, .main p, .main li, .main span, .main label,
    .main .stMarkdown, .main h2, .main h3, .main h4 {{
        color: {COLOR_TEXT};
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{
        background: transparent;
        height: 0;
    }}

    /* ---- Fixed top navigation ---- */
    .alora-topnav {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999999;
        background: linear-gradient(90deg, {COLOR_DEEP_NAVY} 0%, #062456 50%, {COLOR_DEEP_NAVY} 100%);
        border-bottom: 1px solid rgba(20, 217, 229, 0.25);
        box-shadow: 0 4px 24px rgba(4, 27, 77, 0.35);
        height: 64px;
    }}

    .topnav-inner {{
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        max-width: 1140px;
        margin: 0 auto;
        padding: 0 1.25rem;
        height: 64px;
    }}

    .topnav-logo {{
        justify-self: start;
        display: flex;
        align-items: center;
    }}

    .topnav-logo img {{
        height: 46px;
        width: auto;
        object-fit: contain;
        filter: drop-shadow(0 2px 6px rgba(0,0,0,0.2));
    }}

    .topnav-title {{
        justify-self: center;
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        white-space: nowrap;
    }}

    .topnav-title .name-alora {{
        color: {COLOR_WHITE};
    }}

    .topnav-title .name-ai {{
        color: {COLOR_ELECTRIC_CYAN};
    }}

    .topnav-right {{
        justify-self: end;
        width: 120px;
    }}

    /* ---- Sidebar ---- */
    section[data-testid="stSidebar"] > div {{
        background: linear-gradient(180deg, {COLOR_DEEP_NAVY} 0%, #051633 100%);
        padding-top: 4rem;
    }}

    section[data-testid="stSidebar"] .sidebar-block {{
        margin-bottom: 1.25rem;
        padding: 0 0.15rem;
    }}

    section[data-testid="stSidebar"] .sidebar-block-title {{
        color: {COLOR_ELECTRIC_CYAN};
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 0 0 0.65rem 0;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }}

    section[data-testid="stSidebar"] .sidebar-item {{
        color: rgba(255, 255, 255, 0.92);
        font-size: 0.86rem;
        line-height: 1.5;
        padding: 0.35rem 0 0.35rem 1.5rem;
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
        margin: 1.1rem 0;
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
        margin-top: 1.5rem;
        padding-top: 1rem;
        border-top: 1px solid rgba(255,255,255,0.1);
    }}

    /* ---- Dashboard cards ---- */
    .dashboard-hero {{
        background: linear-gradient(135deg, {COLOR_DEEP_NAVY} 0%, #0a3d5c 100%);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        color: {COLOR_WHITE};
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(4, 27, 77, 0.22);
    }}

    .dashboard-hero h2 {{
        color: {COLOR_WHITE} !important;
        margin: 0 0 0.35rem 0;
        font-size: 1.5rem;
    }}

    .dashboard-hero p {{
        color: rgba(255,255,255,0.88);
        margin: 0;
        font-size: 0.95rem;
    }}

    .workspace-card {{
        background: {COLOR_WHITE};
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        box-shadow: 0 2px 16px rgba(4, 27, 77, 0.08);
        border: 1px solid rgba(4, 27, 77, 0.06);
        margin-bottom: 1rem;
    }}

    .multimodal-strip {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        margin: 1rem 0 0 0;
    }}

    .multimodal-chip {{
        background: rgba(20, 217, 229, 0.15);
        border: 1px solid rgba(20, 217, 229, 0.4);
        color: {COLOR_ELECTRIC_CYAN};
        border-radius: 999px;
        padding: 0.35rem 0.85rem;
        font-size: 0.8rem;
        font-weight: 600;
    }}

    /* ---- Metrics ---- */
    .metric-card {{
        background: {COLOR_WHITE};
        border-left: 4px solid {COLOR_ELECTRIC_CYAN};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 2px 12px rgba(4, 27, 77, 0.06);
        margin-bottom: 0.75rem;
    }}

    .metric-card h4 {{
        color: {COLOR_DEEP_NAVY};
        margin: 0 0 0.25rem 0;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .metric-card p {{
        color: {COLOR_TEAL};
        margin: 0;
        font-size: 1.45rem;
        font-weight: 700;
    }}

    /* ---- Pill tabs ---- */
    .pill-nav-hint {{
        color: {COLOR_DEEP_NAVY};
        font-size: 0.9rem;
        margin: 0 0 1rem 0;
    }}

    .pill-nav-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-bottom: 0.5rem;
    }}

    div[data-testid="column"] .pill-nav-row + div button,
    .pill-nav-grid [data-testid="column"] button {{
        border-radius: 999px !important;
        min-height: 2.5rem;
        font-weight: 600;
        font-size: 0.82rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}

    .pill-nav-grid [data-testid="column"] button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(4, 27, 77, 0.15);
    }}

    .pill-nav-grid [data-testid="column"] button[kind="primary"] {{
        background: linear-gradient(135deg, {COLOR_DEEP_NAVY}, #0a3d6e) !important;
        color: {COLOR_WHITE} !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(4, 27, 77, 0.25);
    }}

    .pill-nav-grid [data-testid="column"] button[kind="secondary"] {{
        background: linear-gradient(135deg, {COLOR_DEEP_NAVY}, #0a3d6e) !important;
        color: {COLOR_WHITE} !important;
        border: 1px solid rgba(20, 217, 229, 0.35) !important;
        opacity: 0.88;
    }}

    .pill-nav-grid [data-testid="column"] button[kind="secondary"]:hover {{
        opacity: 1;
        border-color: {COLOR_ELECTRIC_CYAN} !important;
    }}

    /* ---- Viewer workspace ---- */
    .viewer-header {{
        background: linear-gradient(135deg, #eef9fb 0%, #f8fbfd 100%);
        border-radius: 14px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 1.25rem;
        border-left: 5px solid {COLOR_ELECTRIC_CYAN};
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

    .auditory-focus .main .block-container {{
        max-width: 900px;
    }}

    .auditory-focus [data-testid="stVerticalBlock"] > div {{
        margin-bottom: 0.5rem;
    }}

    .sub-pill-row [data-testid="column"] button {{
        border-radius: 999px !important;
        font-size: 0.78rem !important;
        min-height: 2.2rem !important;
    }}

    .main th {{
        background: {COLOR_DEEP_NAVY};
        color: {COLOR_WHITE};
    }}

    .main td {{
        border: 1px solid {COLOR_SILVER};
        color: {COLOR_TEXT};
    }}

    @media (max-width: 768px) {{
        .topnav-title {{ font-size: 1.25rem; }}
        .topnav-logo img {{ height: 38px; }}
        .main .block-container {{ padding-top: 4rem; }}
    }}
    </style>
    """
