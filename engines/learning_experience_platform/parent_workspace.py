"""Parent workspace — progress & encouragement only; never alters curriculum."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics
from engines.learning_experience_platform.collab_store import load_workspace_notes, save_workspace_note
from engines.learning_experience_platform.collaboration import add_comment, list_comments
from engines.learning_experience_platform.permissions import require
from engines.learning_experience_platform.session_store import load_progress


def parent_workspace(
    *,
    parent_id: str,
    learner_id: str,
    lesson_id: str,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    gate = require("parent", "view_learner_progress")
    if not gate["ok"]:
        return gate
    context = context or {}
    outputs = context.get("engine_outputs") or {}
    aie = (outputs.get("accessibility") or {}).get("payload") or {}
    lmas = (outputs.get("learning_motivation") or outputs.get("gamification") or {}).get("payload") or {}

    progress = load_progress(learner_id, lesson_id)
    teacher_comments = list_comments(lesson_id, viewer_id=parent_id, viewer_role="parent")

    home_suggestions = [
        {
            "source": "policy",
            "text": "Review teacher comments and practice verified flashcards — do not invent new curriculum at home.",
        }
    ]

    planner = {}
    try:
        from engines.assessment_mastery_engine.service import api_generate_revision_plan

        planner = api_generate_revision_plan(learner_id, topic=str(context.get("topic") or ""))
    except Exception:  # noqa: BLE001
        planner = {"ok": False}

    achievements = lmas.get("achievements") or lmas.get("xp") or {}
    notes = load_workspace_notes("parent", parent_id, lesson_id)

    analytics.track("parent_engagement", learner_id=learner_id, lesson_id=lesson_id, payload={"parent_id": parent_id})
    return {
        "ok": True,
        "workspace": "parent",
        "learner_id": learner_id,
        "lesson_id": lesson_id,
        "progress": progress,
        "teacher_comments": teacher_comments.get("comments") or [],
        "home_learning_notes": notes,
        "home_learning_suggestions": home_suggestions,
        "accessibility_supports": aie.get("learner_profile") or aie.get("recommendations") or {},
        "revision_planner": planner,
        "achievements": achievements,
        "reading_habits": {
            "time_spent_seconds": progress.get("time_spent_seconds"),
            "reading_pct": progress.get("reading_pct"),
            "resume_anchor": progress.get("resume_anchor"),
        },
        "policy": {
            "never_alter_curriculum": True,
            "encouragement_only": True,
        },
    }


def parent_encouragement(parent_id: str, lesson_id: str, body: str, learner_id: str = "") -> dict[str, Any]:
    gate = require("parent", "encouragement")
    if not gate["ok"]:
        return gate
    return add_comment(
        lesson_id=lesson_id,
        author_id=parent_id,
        author_role="parent",
        body=body,
        target_type="general",
        audience="selected_students",
        audience_ids=[learner_id] if learner_id else [],
    )


def parent_home_note(parent_id: str, lesson_id: str, text: str) -> dict[str, Any]:
    gate = require("parent", "home_learning_notes")
    if not gate["ok"]:
        return gate
    note = save_workspace_note("parent", parent_id, {
        "lesson_id": lesson_id,
        "kind": "home_learning",
        "text": text,
        "curriculum_locked": True,
    })
    return {"ok": True, "note": note}


def parent_mark_practice(parent_id: str, lesson_id: str, activity_id: str = "") -> dict[str, Any]:
    gate = require("parent", "mark_practice")
    if not gate["ok"]:
        return gate
    note = save_workspace_note("parent", parent_id, {
        "lesson_id": lesson_id,
        "kind": "practice_complete",
        "activity_id": activity_id or "home_practice",
    })
    return {"ok": True, "marked": note}
