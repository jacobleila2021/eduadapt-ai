"""Phase 4 experience settings + personalization (synced prefs)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

from engines.learning_experience_platform.phase4_schemas import PremiumSettings, SUPPORTED_UI_LOCALES
from engines.learning_experience_platform.session_store import load_preferences, save_preferences

SETTINGS_DIR = DATA_DIR / "lxp" / "settings"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(learner_id: str) -> Path:
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in learner_id)[:80]
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    return SETTINGS_DIR / f"{safe}.json"


def load_premium_settings(learner_id: str) -> dict[str, Any]:
    path = _path(learner_id)
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    base = PremiumSettings().to_dict()
    # Merge Phase 1 reader prefs
    prefs = load_preferences(learner_id)
    base["theme"] = prefs.get("theme") or base["theme"]
    base["font_family"] = prefs.get("font_family") or base["font_family"]
    base["font_size_px"] = int(prefs.get("font_size_px") or base["font_size_px"])
    path.write_text(json.dumps(base, indent=2), encoding="utf-8")
    return base


def save_premium_settings(learner_id: str, patch: dict[str, Any]) -> dict[str, Any]:
    current = load_premium_settings(learner_id)
    if "language" in patch and patch["language"] not in SUPPORTED_UI_LOCALES:
        patch = {**patch, "language": current.get("language") or "en"}
    updated = {**current, **patch, "updated_at": _now()}
    _path(learner_id).write_text(json.dumps(updated, indent=2, ensure_ascii=False), encoding="utf-8")
    # Mirror theme/font into Phase 1 prefs for continuity
    save_preferences(
        learner_id,
        {
            "theme": updated.get("theme"),
            "font_family": updated.get("font_family"),
            "font_size_px": updated.get("font_size_px"),
            "high_contrast": updated.get("high_contrast"),
            "reduce_motion": updated.get("reduce_motion"),
        },
    )
    return {"ok": True, "settings": updated, "sync_across_devices": True}


def notification_preferences(learner_id: str) -> dict[str, Any]:
    s = load_premium_settings(learner_id)
    return {
        "ok": True,
        "enabled": bool(s.get("notifications_enabled", True)),
        "channels": {
            "lesson_reminders": True,
            "revision_reminders": True,
            "teacher_comments": True,
            "parent_messages": True,
            "companion_updates": bool(s.get("companion_enabled", True)),
            "achievement_unlocks": True,
            "offline_sync_status": True,
            "system_announcements": True,
        },
    }
