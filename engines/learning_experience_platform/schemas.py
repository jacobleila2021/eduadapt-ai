"""LXP schemas — reader session, annotations, themes (presentation only)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

READING_MODES = ("continuous_scroll", "paged", "focus", "fullscreen")
THEMES = ("light", "dark", "sepia", "high_contrast")
HIGHLIGHT_COLORS = ("yellow", "green", "blue", "pink")


@dataclass
class ReaderPreferences:
    theme: str = "light"
    reading_mode: str = "continuous_scroll"
    font_family: str = "Lexend"
    font_size_px: int = 18
    line_spacing: float = 1.6
    word_spacing: float = 0.05
    paragraph_spacing: float = 1.2
    reading_ruler: bool = False
    split_ai_panel: bool = True
    left_nav_open: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ReadingProgress:
    lesson_id: str
    completion_pct: float = 0.0
    reading_pct: float = 0.0
    estimated_minutes: float = 0.0
    time_spent_seconds: float = 0.0
    resume_offset: int = 0
    resume_anchor: str = ""
    last_viewed_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Note:
    note_id: str
    lesson_id: str
    text: str
    category: str = "general"
    anchor: str = ""
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Highlight:
    highlight_id: str
    lesson_id: str
    color: str = "yellow"
    label: str = ""
    target_type: str = "text"  # text|formula|table|diagram
    anchor: str = ""
    excerpt: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Bookmark:
    bookmark_id: str
    lesson_id: str
    target_type: str = "lesson"  # lesson|paragraph|diagram|formula
    anchor: str = ""
    folder: str = "default"
    label: str = ""
    created_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
