"""Phase 3 dashboards — role-scoped workspace summaries."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.parent_workspace import parent_workspace
from engines.learning_experience_platform.permissions import normalize_role
from engines.learning_experience_platform.special_educator_workspace import special_educator_workspace
from engines.learning_experience_platform.teacher_workspace import teacher_workspace


def workspace_dashboard(
    role: str,
    *,
    user_id: str,
    learner_id: str = "",
    lesson_id: str = "",
    learner_ids: list[str] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    role = normalize_role(role)
    if role == "teacher":
        return teacher_workspace(teacher_id=user_id, lesson_id=lesson_id, learner_ids=learner_ids, context=context)
    if role == "parent":
        return parent_workspace(parent_id=user_id, learner_id=learner_id or user_id, lesson_id=lesson_id, context=context)
    if role == "special_educator":
        return special_educator_workspace(educator_id=user_id, learner_id=learner_id, lesson_id=lesson_id, context=context)
    return {
        "ok": True,
        "workspace": "student",
        "hint": "Use revision_mode / exam_mode / flashcards for learner tools",
        "learner_id": learner_id or user_id,
        "lesson_id": lesson_id,
    }
