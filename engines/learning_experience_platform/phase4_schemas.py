"""LXP Phase 4 — premium experience schemas (presentation only)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

SUPPORTED_UI_LOCALES = ("en", "hi", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa", "ur")
# Curriculum translation only when approved bundle exists — never auto-translate verified content
CURRICULUM_TRANSLATION_POLICY = "approved_bundles_only"

BREAKPOINTS = {
    "mobile": 480,
    "tablet": 768,
    "laptop": 1024,
    "desktop": 1280,
    "whiteboard": 1920,
    "foldable": 900,
}

ANIMATION_PRESETS = (
    "page_transition",
    "lesson_transition",
    "ai_response",
    "expand_collapse",
    "drawer",
    "card_hover",
    "progress",
    "read_along",
    "xp_celebration",
    "achievement_unlock",
    "companion_reaction",
    "notification",
)

GESTURES = (
    "swipe_nav",
    "pinch_zoom",
    "long_press",
    "drag_drop_notes",
    "touch_highlight",
    "gesture_bookmark",
    "double_tap_zoom",
    "haptic",
)


@dataclass
class PremiumSettings:
    theme: str = "light"
    language: str = "en"
    font_family: str = "Lexend"
    font_size_px: int = 18
    reduce_motion: bool = False
    high_contrast: bool = False
    audio_enabled: bool = True
    companion_enabled: bool = True
    notifications_enabled: bool = True
    offline_storage_mb: int = 256
    privacy_analytics: bool = True
    sync_auto: bool = True
    rtl_ready: bool = True  # layout hooks for future RTL

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SyncStatus:
    state: str = "idle"  # idle|syncing|synced|conflict|error|offline
    pending: int = 0
    last_synced_at: str = ""
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    retries: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
