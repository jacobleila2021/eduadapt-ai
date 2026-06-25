"""
Landing-page-only palette sample — does not affect workspace or global theme.
"""

LANDING_NAV = "#334155"
LANDING_PRIMARY = "#0F766E"
LANDING_SECONDARY = "#7DD3C7"
LANDING_CELEBRATION = "#F472B6"
LANDING_SURFACE = "#F4E9D8"


def get_landing_sample_css() -> str:
    return f"""
    <style>
    /* ---- Landing sample scope only (marker div present on dashboard) ---- */
    .main .block-container:has(.landing-page-marker) {{
        background: {LANDING_SURFACE} !important;
        border-radius: 18px;
        padding-left: 2rem;
        padding-right: 2rem;
    }}

    .landing-page-marker {{ display: none; }}

    .landing-nav {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem 1.25rem;
        background: {LANDING_NAV};
        border-radius: 14px;
        padding: 0.85rem 1.35rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 6px 20px rgba(51, 65, 85, 0.22);
    }}

    .landing-nav a, .landing-nav span {{
        color: rgba(255, 255, 255, 0.92);
        font-size: 0.88rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        text-decoration: none;
    }}

    .landing-nav .landing-nav-active {{
        color: {LANDING_SECONDARY};
        border-bottom: 2px solid {LANDING_SECONDARY};
        padding-bottom: 0.15rem;
    }}

    .landing-hero {{
        background: linear-gradient(145deg, {LANDING_NAV} 0%, #475569 100%);
        border-radius: 18px;
        padding: 1.85rem 2.15rem;
        color: #fff;
        margin-bottom: 1.35rem;
        box-shadow: 0 10px 32px rgba(51, 65, 85, 0.28);
        border: 1px solid rgba(125, 211, 199, 0.35);
    }}

    .landing-hero h2 {{
        color: #fff !important;
        margin: 0.65rem 0 0.45rem 0;
        font-size: 1.75rem;
        letter-spacing: -0.02em;
    }}

    .landing-hero p {{
        color: rgba(255, 255, 255, 0.9);
        margin: 0;
        font-size: 1rem;
        line-height: 1.55;
    }}

    .landing-badge {{
        display: inline-block;
        background: {LANDING_CELEBRATION};
        color: #fff;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 0.35rem 0.85rem;
        border-radius: 999px;
        box-shadow: 0 4px 14px rgba(244, 114, 182, 0.45);
    }}

    .landing-chip {{
        background: rgba(125, 211, 199, 0.22);
        border: 1px solid {LANDING_SECONDARY};
        color: #ecfdf5;
        border-radius: 999px;
        padding: 0.4rem 0.95rem;
        font-size: 0.82rem;
        font-weight: 600;
    }}

    .landing-palette-strip {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1.15rem;
    }}

    .landing-swatch {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.22);
        border-radius: 999px;
        padding: 0.28rem 0.75rem 0.28rem 0.35rem;
        font-size: 0.72rem;
        font-weight: 600;
        color: rgba(255, 255, 255, 0.95);
    }}

    .landing-swatch-dot {{
        width: 14px;
        height: 14px;
        border-radius: 50%;
        border: 2px solid rgba(255, 255, 255, 0.55);
        flex-shrink: 0;
    }}

    .landing-card {{
        background: #fffef9;
        border: 1px solid rgba(51, 65, 85, 0.12);
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        box-shadow: 0 4px 18px rgba(51, 65, 85, 0.08);
        margin-bottom: 1.35rem;
    }}

    .landing-section-title {{
        color: {LANDING_NAV} !important;
        font-size: 1.25rem;
        font-weight: 700;
        margin: 0 0 1rem 0;
        letter-spacing: -0.01em;
    }}

    .landing-metric-card {{
        background: {LANDING_SURFACE};
        border-left: 4px solid {LANDING_SECONDARY};
        border-radius: 12px;
        padding: 1.1rem 1.35rem;
        box-shadow: 0 2px 10px rgba(51, 65, 85, 0.06);
        margin-bottom: 0.5rem;
    }}

    .landing-metric-card h4 {{
        color: {LANDING_NAV};
        margin: 0 0 0.3rem 0;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}

    .landing-metric-card p {{
        color: {LANDING_PRIMARY};
        margin: 0;
        font-size: 1.5rem;
        font-weight: 700;
    }}

    .landing-achievement {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        background: rgba(244, 114, 182, 0.14);
        border: 1px solid {LANDING_CELEBRATION};
        color: #be185d;
        border-radius: 999px;
        padding: 0.35rem 0.85rem;
        font-size: 0.82rem;
        font-weight: 700;
        margin-top: 0.75rem;
    }}

    .landing-pill-hint {{
        color: {LANDING_NAV};
        font-size: 0.95rem;
        margin: 0 0 1.25rem 0;
        line-height: 1.5;
        font-weight: 500;
    }}

    /* Landing-only buttons (key prefixes) */
    div[class*="st-key-landing_generate"] button {{
        background: {LANDING_PRIMARY} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }}

    div[class*="st-key-landing_generate"] button:hover {{
        background: #0d9488 !important;
        box-shadow: 0 4px 16px rgba(15, 118, 110, 0.35) !important;
    }}

    div[class*="st-key-landing_sample"] button,
    div[class*="st-key-landing_clear"] button {{
        background: {LANDING_SECONDARY} !important;
        color: {LANDING_NAV} !important;
        border: 1px solid rgba(51, 65, 85, 0.15) !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }}

    /* Dashboard adaptation pills only — not workspace (ws_pill_) */
    div[class*="st-key-pill_"]:not([class*="st-key-ws_pill_"]) button {{
        background: {LANDING_PRIMARY} !important;
        color: #fff !important;
        border: 2px solid rgba(125, 211, 199, 0.65) !important;
        border-radius: 999px !important;
        min-height: 3.5rem !important;
        font-weight: 700 !important;
    }}

    div[class*="st-key-pill_"]:not([class*="st-key-ws_pill_"]) button:hover {{
        background: #0d9488 !important;
        border-color: {LANDING_SECONDARY} !important;
    }}

    div[class*="st-key-pill_"]:not([class*="st-key-ws_pill_"]) button[kind="primary"] {{
        background: {LANDING_NAV} !important;
        border-color: {LANDING_CELEBRATION} !important;
    }}
    </style>
    """
