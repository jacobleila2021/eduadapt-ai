"""
Custom CSS and HTML helpers for the EduAdapt AI interface.
"""

from config import (
    COLOR_BRIGHT_AQUA,
    COLOR_DEEP_NAVY,
    COLOR_ELECTRIC_CYAN,
    COLOR_SILVER,
    COLOR_WHITE,
)


def get_custom_css() -> str:
    """Return Streamlit-compatible CSS for the Omnili / EduAdapt design system."""
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .main .block-container {{
        padding-top: 1rem;
        max-width: 1200px;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* ---- Sidebar (Deep Navy + cyan accents) ---- */
    div[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLOR_DEEP_NAVY} 0%, #021028 100%);
        border-right: 1px solid rgba(20, 217, 229, 0.25);
    }}

    div[data-testid="stSidebar"] * {{
        color: {COLOR_WHITE} !important;
    }}

    div[data-testid="stSidebar"] .stButton > button {{
        background: linear-gradient(135deg, {COLOR_ELECTRIC_CYAN}, {COLOR_BRIGHT_AQUA}) !important;
        color: {COLOR_DEEP_NAVY} !important;
        border: none;
        border-radius: 10px;
        font-weight: 700;
    }}

    div[data-testid="stSidebar"] hr {{
        border-color: rgba(20, 217, 229, 0.3);
    }}

    .sidebar-metric {{
        background: rgba(20, 217, 229, 0.12);
        border: 1px solid rgba(34, 240, 255, 0.35);
        border-radius: 12px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }}

    .sidebar-metric strong {{
        color: {COLOR_BRIGHT_AQUA} !important;
        font-size: 1.15rem;
    }}

    .sidebar-status-ready {{
        background: rgba(20, 217, 229, 0.18);
        border: 1px solid {COLOR_ELECTRIC_CYAN};
        border-radius: 10px;
        padding: 0.65rem 0.85rem;
        text-align: center;
        font-weight: 600;
        color: {COLOR_BRIGHT_AQUA} !important;
    }}

    .sidebar-status-warn {{
        background: rgba(255, 193, 7, 0.12);
        border: 1px solid rgba(255, 193, 7, 0.4);
        border-radius: 10px;
        padding: 0.65rem 0.85rem;
        text-align: center;
        font-weight: 600;
    }}

    /* ---- Main header with logo ---- */
    .brand-header-wrap {{
        background: linear-gradient(135deg, {COLOR_DEEP_NAVY} 0%, #062659 55%, #0a3d6e 100%);
        padding: 1rem 1.25rem;
        border-radius: 16px;
        border: 1px solid rgba(20, 217, 229, 0.35);
        margin-bottom: 0.5rem;
        box-shadow: 0 10px 32px rgba(4, 27, 77, 0.35);
    }}

    .brand-header {{
        display: flex;
        align-items: center;
        gap: 1.25rem;
        background: linear-gradient(135deg, {COLOR_DEEP_NAVY} 0%, #062659 55%, #0a3d6e 100%);
        padding: 1.25rem 1.75rem;
        border-radius: 16px;
        border: 1px solid rgba(20, 217, 229, 0.35);
        margin-bottom: 1.25rem;
        box-shadow: 0 10px 32px rgba(4, 27, 77, 0.45);
    }}

    .brand-header-text h1 {{
        margin: 0;
        font-size: 1.85rem;
        font-weight: 700;
        color: {COLOR_WHITE} !important;
    }}

    .brand-tagline {{
        margin: 0.35rem 0 0 0;
        font-size: 1.05rem;
        color: {COLOR_ELECTRIC_CYAN};
        font-weight: 500;
    }}

    .brand-sub {{
        margin: 0.5rem 0 0 0;
        font-size: 0.92rem;
        color: {COLOR_SILVER};
    }}

    /* ---- Metrics & cards ---- */
    .metric-card {{
        background: {COLOR_WHITE};
        border-left: 4px solid {COLOR_ELECTRIC_CYAN};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 2px 12px rgba(4, 27, 77, 0.1);
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
        color: {COLOR_ELECTRIC_CYAN};
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
    }}

    /* ---- Adaptation expanders (all stay on page) ---- */
    .adapt-panel-hint {{
        color: {COLOR_DEEP_NAVY};
        font-size: 0.95rem;
        margin: 0 0 1rem 0;
        padding: 0.65rem 1rem;
        background: rgba(20, 217, 229, 0.12);
        border-left: 4px solid {COLOR_ELECTRIC_CYAN};
        border-radius: 0 10px 10px 0;
    }}

    div[data-testid="stExpander"] {{
        border: 1px solid rgba(20, 217, 229, 0.35);
        border-radius: 12px;
        margin-bottom: 0.65rem;
        background: #f7fdff;
    }}

    div[data-testid="stExpander"] details summary {{
        background: linear-gradient(90deg, {COLOR_DEEP_NAVY}, #0a3568);
        color: {COLOR_BRIGHT_AQUA} !important;
        font-weight: 700;
        border-radius: 11px;
        padding: 0.15rem 0.5rem;
    }}

    div[data-testid="stExpander"] details[open] summary {{
        border-radius: 11px 11px 0 0;
        border-bottom: 2px solid {COLOR_ELECTRIC_CYAN};
    }}

    /* ---- Streamlit tabs (if used elsewhere) ---- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        flex-wrap: wrap;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: rgba(4, 27, 77, 0.08);
        border-radius: 10px 10px 0 0;
        color: {COLOR_DEEP_NAVY};
        font-weight: 600;
        border: 1px solid rgba(20, 217, 229, 0.25);
    }}

    .stTabs [aria-selected="true"] {{
        background: linear-gradient(180deg, {COLOR_DEEP_NAVY}, #0a3568) !important;
        color: {COLOR_BRIGHT_AQUA} !important;
        border-color: {COLOR_ELECTRIC_CYAN} !important;
    }}

    .main h2, .main h3 {{
        color: {COLOR_DEEP_NAVY};
        margin-top: 1.25rem;
    }}

    .main th {{
        background: {COLOR_DEEP_NAVY};
        color: {COLOR_WHITE};
        padding: 0.5rem 0.75rem;
        text-align: left;
    }}

    .main td {{
        border: 1px solid rgba(20, 217, 229, 0.35);
        padding: 0.5rem 0.75rem;
    }}

    .main svg {{
        max-width: 100%;
        height: auto;
        display: block;
        margin: 1rem auto;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(4, 27, 77, 0.15);
    }}

    div[data-testid="stMain"] .stDownloadButton button {{
        background: linear-gradient(135deg, {COLOR_DEEP_NAVY}, #0a3568);
        color: {COLOR_BRIGHT_AQUA};
        border: 1px solid {COLOR_ELECTRIC_CYAN};
        font-weight: 600;
    }}
    </style>
    """


def render_brand_header(show_logo_path: str | None = None) -> None:
    """Hero with EduAdapt logo in the top-left."""
    st.markdown(
        f'<div class="brand-header-wrap">',
        unsafe_allow_html=True,
    )
    col_logo, col_text = st.columns([1, 4], vertical_alignment="center")
    with col_logo:
        if show_logo_path:
            st.image(show_logo_path, width=150)
    with col_text:
        st.markdown(
            f"""
            <div class="brand-header-text">
                <h1 style="color:{COLOR_WHITE};margin:0;font-size:1.85rem;">EduAdapt AI</h1>
                <p style="color:{COLOR_ELECTRIC_CYAN};margin:0.35rem 0 0 0;font-weight:600;">
                    Upload Once. Teach Every Learner.
                </p>
                <p style="color:{COLOR_SILVER};margin:0.45rem 0 0 0;font-size:0.92rem;">
                    Differentiated lessons for Grades 3–11 — powered by Omnili
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        f'<div style="height:4px;background:linear-gradient(90deg,{COLOR_DEEP_NAVY},{COLOR_ELECTRIC_CYAN},{COLOR_BRIGHT_AQUA});'
        f'border-radius:4px;margin-bottom:1.25rem;"></div>',
        unsafe_allow_html=True,
    )


def render_header() -> str:
    """Legacy HTML header (prefer render_brand_header in app.py)."""
    return f"""
    <div class="brand-header">
        <div class="brand-header-text">
            <h1>EduAdapt AI</h1>
            <p class="brand-tagline">Upload Once. Teach Every Learner.</p>
        </div>
    </div>
    """
