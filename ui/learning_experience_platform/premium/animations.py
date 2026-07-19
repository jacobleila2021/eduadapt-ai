"""Premium motion CSS/JS helpers — respects reduce motion."""

from __future__ import annotations

from typing import Any


def motion_css(*, reduce_motion: bool = False, duration_ms: int = 180) -> str:
    if reduce_motion:
        return """
        <style>
        .lxp-premium *, .lxp-premium *::before, .lxp-premium *::after {
          animation: none !important; transition: none !important; scroll-behavior: auto !important;
        }
        </style>
        """
    d = max(80, min(int(duration_ms), 280))
    return f"""
    <style>
    @media (prefers-reduced-motion: reduce) {{
      .lxp-premium *, .lxp-premium *::before, .lxp-premium *::after {{
        animation: none !important; transition: none !important;
      }}
    }}
    .lxp-premium .lxp-fade {{ animation: lxpFade {d}ms ease-out; }}
    .lxp-premium .lxp-slide-in {{ animation: lxpSlide {d}ms ease-out; }}
    .lxp-premium .lxp-panel {{ transition: max-height {d}ms ease, opacity {d}ms ease; }}
    .lxp-premium .lxp-card:hover {{ transform: translateY(-1px); transition: transform {d}ms ease; }}
    .lxp-premium .lxp-progress-bar {{ transition: width {d}ms linear; }}
    .lxp-premium .lxp-readalong-word.active {{ background: rgba(47,111,94,.18); transition: background {d}ms; }}
    .lxp-premium .lxp-xp-pop {{ animation: lxpPop {d + 40}ms ease-out; }}
    .lxp-premium .lxp-notify {{ animation: lxpSlide {d}ms ease-out; }}
    @keyframes lxpFade {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    @keyframes lxpSlide {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
    @keyframes lxpPop {{ 0% {{ transform: scale(.92); opacity: 0; }} 100% {{ transform: scale(1); opacity: 1; }} }}
    </style>
    """


def animation_catalog() -> dict[str, Any]:
    return {
        "page_transition": "lxp-fade",
        "lesson_transition": "lxp-slide-in",
        "ai_response": "lxp-fade",
        "expand_collapse": "lxp-panel",
        "drawer": "lxp-slide-in",
        "card_hover": "lxp-card",
        "progress": "lxp-progress-bar",
        "read_along": "lxp-readalong-word",
        "xp_celebration": "lxp-xp-pop",
        "achievement_unlock": "lxp-xp-pop",
        "companion_reaction": "lxp-fade",
        "notification": "lxp-notify",
        "policy": {"optional": True, "never_delay_content": True},
    }
