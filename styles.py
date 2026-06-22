"""
Custom CSS and HTML helpers for the EduAdapt AI interface.
"""

from config import COLOR_DARK_BLUE, COLOR_TEAL, COLOR_SILVER, COLOR_WHITE


def get_custom_css() -> str:
    """
    Return Streamlit-compatible CSS for the EdTech design system.
    Injected once at the top of the app via st.markdown.
    """
    return f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    .main .block-container {{
        padding-top: 1.5rem;
        max-width: 1100px;
    }}

    /* Hide default Streamlit header/footer clutter */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    .edu-header {{
        background: linear-gradient(135deg, {COLOR_DARK_BLUE} 0%, {COLOR_TEAL} 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        color: {COLOR_WHITE};
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 24px rgba(11, 46, 89, 0.25);
    }}

    .edu-header h1 {{
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        color: {COLOR_WHITE} !important;
    }}

    .edu-tagline {{
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.95;
        color: {COLOR_SILVER};
    }}

    .metric-card {{
        background: {COLOR_WHITE};
        border-left: 4px solid {COLOR_TEAL};
        border-radius: 12px;
        padding: 1rem 1.25rem;
        box-shadow: 0 2px 12px rgba(11, 46, 89, 0.08);
        margin-bottom: 0.75rem;
    }}

    .metric-card h4 {{
        color: {COLOR_DARK_BLUE};
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

    .sidebar-metric {{
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        text-align: center;
    }}

    .content-card {{
        background: #f8fafb;
        border: 1px solid {COLOR_SILVER};
        border-radius: 12px;
        padding: 1.5rem;
        line-height: 1.7;
    }}

    div[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLOR_DARK_BLUE} 0%, #0a2540 100%);
    }}

    div[data-testid="stSidebar"] * {{
        color: {COLOR_WHITE} !important;
    }}

    div[data-testid="stSidebar"] .stButton > button {{
        background: {COLOR_TEAL};
        color: {COLOR_WHITE};
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background-color: #eef4f8;
        border-radius: 8px 8px 0 0;
        color: {COLOR_DARK_BLUE};
        font-weight: 500;
    }}

    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_TEAL} !important;
        color: {COLOR_WHITE} !important;
    }}

    /* Rich lesson content: vocabulary cards, colored boxes, diagrams */
    .main svg {{
        max-width: 100%;
        height: auto;
        display: block;
        margin: 1rem auto;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(11, 46, 89, 0.12);
    }}

    .main table {{
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }}

    .main th {{
        background: {COLOR_DARK_BLUE};
        color: {COLOR_WHITE};
        padding: 0.5rem 0.75rem;
        text-align: left;
    }}

    .main td {{
        border: 1px solid {COLOR_SILVER};
        padding: 0.5rem 0.75rem;
    }}

    .main h2, .main h3 {{
        color: {COLOR_DARK_BLUE};
        margin-top: 1.25rem;
    }}

    .adapt-nav-hint {{
        color: #5a6b7d;
        font-size: 0.92rem;
        margin: 0 0 0.75rem 0;
    }}

    .adapt-nav-grid [data-testid="column"] button {{
        min-height: 3.25rem;
        white-space: normal;
        line-height: 1.25;
        font-size: 0.82rem;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.45rem 0.35rem;
    }}

    .adapt-nav-grid [data-testid="column"] button[kind="primary"] {{
        background: {COLOR_TEAL} !important;
        border: 2px solid {COLOR_TEAL} !important;
        box-shadow: 0 2px 8px rgba(0, 140, 149, 0.35);
    }}

    .adapt-nav-grid [data-testid="column"] button[kind="secondary"] {{
        background: #eef4f8 !important;
        color: {COLOR_DARK_BLUE} !important;
        border: 1px solid #c8d8e4 !important;
    }}

    .sidebar-status-ready {{
        background: rgba(0, 140, 149, 0.25);
        border: 1px solid rgba(0, 200, 210, 0.45);
        border-radius: 10px;
        padding: 0.65rem 0.85rem;
        text-align: center;
        font-weight: 600;
        font-size: 0.9rem;
    }}

    .sidebar-status-warn {{
        background: rgba(255, 193, 7, 0.15);
        border: 1px solid rgba(255, 193, 7, 0.35);
        border-radius: 10px;
        padding: 0.65rem 0.85rem;
        text-align: center;
        font-weight: 600;
        font-size: 0.9rem;
    }}
    </style>
    """


def render_header() -> str:
    """Return HTML for the main page hero header."""
    return """
    <div class="edu-header">
        <h1>EduAdapt AI</h1>
        <p class="edu-tagline">Upload Once. Teach Every Learner.</p>
        <p style="margin-top:0.75rem; font-size:0.95rem; opacity:0.9;">
            Differentiated lessons for Grades 3–11 in under 2 minutes.
        </p>
    </div>
    """
