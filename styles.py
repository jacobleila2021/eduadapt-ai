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

    /* ---- Teal / cyan pill tabs (WCAG contrast) ---- */
    .pill-nav-hint {{
        color: #3d5470;
        font-size: 0.92rem;
        margin: 0 0 1.15rem 0;
        line-height: 1.5;
    }}

    .pill-nav-grid [data-testid="column"] button {{
        border-radius: 999px !important;
        min-height: 2.75rem !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.01em;
    }}

    .pill-nav-grid [data-testid="column"] button[kind="secondary"] {{
        background: {COLOR_ELECTRIC_CYAN} !important;
        color: {COLOR_DEEP_NAVY} !important;
        border: 2px solid {COLOR_ELECTRIC_CYAN} !important;
    }}

    .pill-nav-grid [data-testid="column"] button[kind="secondary"]:hover {{
        background: {COLOR_BRIGHT_AQUA} !important;
        border-color: {COLOR_BRIGHT_AQUA} !important;
        color: {COLOR_DEEP_NAVY} !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(20, 217, 229, 0.45);
    }}

    .pill-nav-grid [data-testid="column"] button[kind="primary"] {{
        background: {COLOR_DEEP_NAVY} !important;
        color: {COLOR_WHITE} !important;
        border: 2px solid {COLOR_ELECTRIC_CYAN} !important;
        box-shadow: 0 0 22px rgba(20, 217, 229, 0.55), 0 4px 16px rgba(4, 27, 77, 0.3);
    }}

    .pill-nav-grid [data-testid="column"] button[kind="primary"]:hover {{
        box-shadow: 0 0 28px rgba(34, 240, 255, 0.65), 0 6px 20px rgba(4, 27, 77, 0.35);
        transform: translateY(-2px);
    }}

    .sub-pill-row [data-testid="column"] button[kind="secondary"] {{
        background: rgba(20, 217, 229, 0.25) !important;
        color: {COLOR_DEEP_NAVY} !important;
        border: 1px solid {COLOR_ELECTRIC_CYAN} !important;
        border-radius: 999px !important;
        font-size: 0.78rem !important;
        min-height: 2.35rem !important;
    }}

    .sub-pill-row [data-testid="column"] button[kind="primary"] {{
        background: {COLOR_TEAL} !important;
        color: {COLOR_WHITE} !important;
        border-radius: 999px !important;
        font-size: 0.78rem !important;
        min-height: 2.35rem !important;
        box-shadow: 0 0 14px rgba(20, 217, 229, 0.4);
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

    @media (max-width: 768px) {{
        .alora-topnav, .topnav-inner {{ height: 100px; }}
        .topnav-title {{ font-size: 1.5rem; }}
        .topnav-logo-img {{ height: 72px; }}
        .topnav-tagline, .topnav-right {{ display: none; }}
        .main .block-container {{ padding-top: 6.75rem; }}
    }}
    </style>
    """
