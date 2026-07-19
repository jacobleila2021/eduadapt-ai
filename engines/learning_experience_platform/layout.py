"""Reader layout model — panels, toolbar, footer (UI-agnostic)."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.navigation import breadcrumbs, build_toc, navigation_state
from engines.learning_experience_platform.themes import reading_mode_css, resolve_theme


def build_layout(
    lesson: dict[str, Any] | None = None,
    *,
    prefs: dict[str, Any] | None = None,
    progress: dict[str, Any] | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    lesson = lesson or {}
    prefs = prefs or {}
    progress = progress or {}
    meta = meta or {}
    toc = build_toc(lesson)
    nav = navigation_state(toc, resume_anchor=str(progress.get("resume_anchor") or ""))
    theme = resolve_theme(prefs.get("theme") or "light")
    mode = reading_mode_css(prefs.get("reading_mode") or "continuous_scroll")
    return {
        "responsive": {"desktop": True, "tablet": True, "mobile": True, "split_screen": True},
        "panels": {
            "left_nav": {"open": bool(prefs.get("left_nav_open", True)), "toc": toc},
            "reading": {"mode": mode, "content_keys": list(lesson.keys())[:20]},
            "right_ai": {"open": bool(prefs.get("split_ai_panel", True)), "collapsible": True},
        },
        "toolbar": {
            "sticky": True,
            "actions": ["theme", "font", "mode", "audio", "search", "bookmark", "notes", "offline"],
        },
        "footer": {
            "progress_pct": progress.get("reading_pct") or 0,
            "time_spent_seconds": progress.get("time_spent_seconds") or 0,
            "estimated_minutes": progress.get("estimated_minutes") or 0,
        },
        "breadcrumbs": breadcrumbs(
            board=str(meta.get("board") or ""),
            grade=str(meta.get("grade") or ""),
            subject=str(meta.get("subject") or ""),
            chapter=str(meta.get("chapter") or ""),
            topic=str(meta.get("topic") or lesson.get("title") or ""),
        ),
        "navigation": nav,
        "theme": theme,
        "distraction_free": mode.get("focus_distraction_free"),
    }
