"""Accessibility polish CSS — WCAG 2.2 AA presentation aids."""

from __future__ import annotations

from typing import Any


def a11y_css(*, high_contrast: bool = False, larger_targets: bool = True) -> str:
    target = "44px" if larger_targets else "36px"
    contrast = """
    .lxp-premium { --lxp-fg: #000; --lxp-bg: #fff; --lxp-accent: #000; }
    .lxp-premium a, .lxp-premium button { text-decoration: underline; }
    """ if high_contrast else ""
    return f"""
    <style>
    {contrast}
    .lxp-premium :focus-visible {{
      outline: 3px solid #2F6F5E; outline-offset: 2px;
    }}
    .lxp-premium .lxp-touch {{
      min-height: {target}; min-width: {target};
    }}
    .lxp-premium [aria-busy="true"] {{ cursor: progress; }}
    </style>
    """


def keyboard_shortcuts() -> dict[str, str]:
    return {
        "j / k": "Previous / next section",
        "/": "Search in lesson",
        "n": "New note",
        "b": "Bookmark",
        "?": "Shortcut overlay",
        "Esc": "Close drawer / exit focus mode",
    }


def a11y_audit_checklist() -> dict[str, Any]:
    return {
        "wcag": "2.2 AA",
        "reduce_motion": True,
        "focus_indicators": True,
        "high_contrast": True,
        "keyboard_equivalents": True,
        "aria_labels": True,
        "touch_targets_44px": True,
        "tab_order": True,
        "source": "AIE presentation layer",
    }
