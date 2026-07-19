"""Companion library & selection — teachers/learners configure; never invents curriculum."""

from __future__ import annotations

from typing import Any

from engines.learning_companion_engine.schemas import COMPANION_LIBRARY, PERSONALITY_STYLES


def list_companions() -> list[dict[str, Any]]:
    return [{"id": k, **v} for k, v in COMPANION_LIBRARY.items()]


def get_companion(companion_id: str) -> dict[str, Any]:
    cid = companion_id if companion_id in COMPANION_LIBRARY else "study_panda"
    return {"id": cid, **COMPANION_LIBRARY[cid]}


def select_companion(learner_id: str, companion_id: str, *, teacher_allowed: list[str] | None = None) -> dict[str, Any]:
    if teacher_allowed and companion_id not in teacher_allowed:
        return {"ok": False, "error": "companion_not_allowed_by_teacher", "allowed": teacher_allowed}
    companion = get_companion(companion_id)
    return {"ok": True, "learner_id": learner_id, "companion": companion}


def validate_style(style: str) -> str:
    return style if style in PERSONALITY_STYLES else "gentle_coach"
