"""Teacher workspace — lesson-integrated teaching tools (no curriculum invention)."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics
from engines.learning_experience_platform.collab_store import load_workspace_notes, save_workspace_note
from engines.learning_experience_platform.collaboration import add_comment, list_comments
from engines.learning_experience_platform.permissions import require
from engines.learning_experience_platform.session_store import load_progress
from engines.learning_experience_platform.shared_annotations import add_shared_annotation


def teacher_workspace(
    *,
    teacher_id: str,
    lesson_id: str,
    learner_ids: list[str] | None = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    gate = require("teacher", "view_class_progress")
    if not gate["ok"]:
        return gate
    context = context or {}
    learner_ids = list(learner_ids or [])
    outputs = context.get("engine_outputs") or {}
    aie = (outputs.get("accessibility") or {}).get("payload") or {}
    atie = (outputs.get("ai_tutor") or {}).get("payload") or {}
    ame = (outputs.get("assessment") or {}).get("payload") or {}

    completion = []
    for lid in learner_ids[:40]:
        prog = load_progress(lid, lesson_id)
        completion.append({
            "learner_id": lid,
            "reading_pct": prog.get("reading_pct"),
            "time_spent_seconds": prog.get("time_spent_seconds"),
        })

    # Optional AME / ALE dashboards
    class_dash = {}
    try:
        from engines.assessment_mastery_engine.service import api_dashboards

        class_dash = api_dashboards("teacher", learner_ids=learner_ids)
    except Exception:  # noqa: BLE001
        class_dash = {"ok": False, "fallback": True}

    notes = load_workspace_notes("teacher", teacher_id, lesson_id)
    comments = list_comments(lesson_id, viewer_id=teacher_id, viewer_role="teacher")

    analytics.track("teacher_workspace", learner_id=teacher_id, lesson_id=lesson_id)
    return {
        "ok": True,
        "workspace": "teacher",
        "lesson_id": lesson_id,
        "capabilities": [
            "view_lesson", "comments", "highlights", "pin_explanations", "teaching_notes",
            "revision_notes", "attach_resources", "approve_adaptations", "lock_sections",
            "assign_activities", "schedule_revision", "checkpoints", "discussion_prompts",
            "track_reading", "track_ai_tutor", "track_revision", "a11y_recommendations",
            "compare_adaptations",
        ],
        "reading_completion": completion,
        "ai_tutor_signal": {"present": bool(atie), "hint": "consume ATIE payloads — do not invent"},
        "accessibility_recommendations": aie.get("recommendations") or aie.get("learner_profile") or {},
        "revision_progress": ame.get("exam_readiness") or {},
        "class_dashboard": class_dash,
        "teaching_notes": notes,
        "comments": comments.get("comments") or [],
        "policy": {"never_alter_verified_sections_without_lock": True},
    }


def teacher_add_teaching_note(teacher_id: str, lesson_id: str, text: str, *, kind: str = "teaching") -> dict[str, Any]:
    gate = require("teacher", "teaching_notes")
    if not gate["ok"]:
        return gate
    note = save_workspace_note("teacher", teacher_id, {
        "lesson_id": lesson_id,
        "kind": kind,
        "text": text,
        "curriculum_locked": True,
    })
    return {"ok": True, "note": note}


def teacher_pin_explanation(teacher_id: str, lesson_id: str, anchor: str, text: str) -> dict[str, Any]:
    gate = require("teacher", "pin_explanation")
    if not gate["ok"]:
        return gate
    return add_shared_annotation(
        lesson_id=lesson_id,
        author_id=teacher_id,
        author_role="teacher",
        annotation_type="sticky_note",
        visibility="shared_classroom",
        payload={"pinned": True, "anchor": anchor, "text": text},
    )


def teacher_publish_comment(**kwargs: Any) -> dict[str, Any]:
    kwargs["author_role"] = "teacher"
    return add_comment(**kwargs)


def teacher_lock_section(teacher_id: str, lesson_id: str, section_id: str) -> dict[str, Any]:
    gate = require("teacher", "lock_section")
    if not gate["ok"]:
        return gate
    note = save_workspace_note("teacher", teacher_id, {
        "lesson_id": lesson_id,
        "kind": "lock",
        "section_id": section_id,
        "text": f"Locked verified section {section_id}",
    })
    return {"ok": True, "lock": note, "note": "Locks presentation edits — verified content unchanged"}


def teacher_assign_activity(teacher_id: str, lesson_id: str, activity: dict[str, Any]) -> dict[str, Any]:
    gate = require("teacher", "assign_activity")
    if not gate["ok"]:
        return gate
    note = save_workspace_note("teacher", teacher_id, {
        "lesson_id": lesson_id,
        "kind": "assignment",
        "activity": activity,
    })
    return {"ok": True, "assignment": note}
