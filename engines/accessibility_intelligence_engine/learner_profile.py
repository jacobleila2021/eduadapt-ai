"""Learner accessibility profile store — functional preferences only."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from knowledge.paths import DATA_DIR

from engines.accessibility_intelligence_engine.schemas import LearnerAccessibilityProfile

AIE_DIR = DATA_DIR / "aie"
PROFILES_DIR = AIE_DIR / "profiles"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(learner_id: str) -> Path:
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in learner_id)[:80]
    return PROFILES_DIR / f"{safe}.json"


def load_profile(learner_id: str) -> LearnerAccessibilityProfile:
    path = _path(learner_id)
    if not path.is_file():
        return LearnerAccessibilityProfile(learner_id=learner_id, active_profiles=["neurotypical"])
    data = json.loads(path.read_text(encoding="utf-8"))
    data["stores_medical_diagnoses"] = False
    return LearnerAccessibilityProfile.from_dict(data)


def save_profile(profile: LearnerAccessibilityProfile) -> Path:
    profile.stores_medical_diagnoses = False
    path = _path(profile.learner_id)
    path.write_text(json.dumps(profile.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def update_preferences(learner_id: str, updates: dict[str, Any]) -> LearnerAccessibilityProfile:
    profile = load_profile(learner_id)
    for k, v in updates.items():
        if k == "stores_medical_diagnoses":
            continue
        if hasattr(profile, k):
            setattr(profile, k, v)
    # merge self-selected
    if "self_selected_preferences" in updates and isinstance(updates["self_selected_preferences"], dict):
        profile.self_selected_preferences.update(updates["self_selected_preferences"])
    profile.accessibility_history.append({"at": _now(), "action": "preferences_updated", "keys": list(updates.keys())})
    save_profile(profile)
    return profile


def build_profile_from_context(context: dict[str, Any]) -> LearnerAccessibilityProfile:
    """Merge explicit context profiles with stored learner profile."""
    learner_id = context.get("learner_id") or context.get("student_id") or "anonymous"
    base = load_profile(learner_id) if learner_id != "anonymous" else LearnerAccessibilityProfile(learner_id=learner_id)
    incoming = context.get("accessibility_profiles") or context.get("profiles") or []
    if isinstance(incoming, str):
        incoming = [incoming]
    if incoming:
        # normalize executive → executive_function
        normed = []
        for p in incoming:
            key = str(p).lower().replace(" ", "_")
            if key in ("executive", "ef"):
                key = "executive_function"
            normed.append(key)
        base.active_profiles = list(dict.fromkeys(normed))
    if context.get("grade"):
        base.grade = str(context["grade"])
    if context.get("reading_level"):
        base.reading_level = str(context["reading_level"])
    # self prefs override
    prefs = context.get("accessibility_preferences") or {}
    if isinstance(prefs, dict):
        for k, v in prefs.items():
            if hasattr(base, k) and k != "stores_medical_diagnoses":
                setattr(base, k, v)
    return base


def list_profile_ids() -> list[str]:
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    return [p.stem for p in PROFILES_DIR.glob("*.json")]
