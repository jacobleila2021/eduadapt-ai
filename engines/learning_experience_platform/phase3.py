"""Phase 3 aggregator — collaboration, workspaces, revision & assessment."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform.ai_revision import ai_revision_assist
from engines.learning_experience_platform.dashboards import workspace_dashboard
from engines.learning_experience_platform.exam_mode import exam_mode
from engines.learning_experience_platform.flashcards import build_flashcards
from engines.learning_experience_platform.formula_sheets import build_formula_sheets
from engines.learning_experience_platform.permissions import normalize_role
from engines.learning_experience_platform.revision_mode import revision_mode
from engines.learning_experience_platform.revision_planner import revision_planner


def build_phase3(context: dict[str, Any]) -> dict[str, Any]:
    learner_id = str(context.get("learner_id") or context.get("user_id") or "anonymous")
    role = normalize_role(str(context.get("role") or "student"))
    lesson = context.get("lesson") or {}
    lesson_id = str(lesson.get("lesson_id") or context.get("lesson_id") or lesson.get("title") or "lesson")
    topic = str(context.get("topic") or lesson.get("title") or "")
    lesson_text = str(lesson.get("body") or context.get("lesson_text") or "")
    exam_active = bool(context.get("exam_mode_active"))

    revision = revision_mode(
        learner_id=learner_id,
        lesson=lesson,
        context=context,
        exam_mode_active=exam_active,
    )
    cards = build_flashcards(lesson=lesson, context=context, learner_id=learner_id)
    formulae = build_formula_sheets(subject=str(context.get("subject") or ""), context=context, lesson=lesson)
    planner = revision_planner(
        learner_id=learner_id,
        exam_days=context.get("exam_days"),
        exam_date=str(context.get("exam_date") or ""),
        topic=topic,
        lesson_text=lesson_text,
        context=context,
        available_minutes_per_day=int(context.get("available_minutes_per_day") or 45),
    )
    exam = exam_mode(
        learner_id=learner_id,
        topic=topic,
        lesson_text=lesson_text,
        mode=str(context.get("exam_ui_mode") or "practice"),
        context=context,
    )
    assist = ai_revision_assist(learner_id=learner_id, action="summarize", context=context)
    dash = workspace_dashboard(
        role,
        user_id=str(context.get("user_id") or learner_id),
        learner_id=learner_id,
        lesson_id=lesson_id,
        learner_ids=list(context.get("learner_ids") or []),
        context=context,
    )

    return {
        "system": "LXP",
        "phase": "phase3_collab_revision_assessment",
        "role": role,
        "revision_mode": revision,
        "flashcards": cards,
        "formula_sheets": formulae,
        "revision_planner": planner,
        "exam_mode": exam,
        "ai_revision": assist,
        "workspace": dash,
        "collaboration": {
            "enabled": True,
            "roles": ["student", "teacher", "parent", "special_educator", "administrator"],
            "apis": ["comments", "shared_annotations", "notifications"],
        },
        "policy": {
            "never_generate_curriculum": True,
            "parents_never_alter_curriculum": True,
            "companion_suppressed_in_exam": True,
            "official_answers_verified_only": True,
            "engines_consumed_not_replaced": True,
        },
    }
