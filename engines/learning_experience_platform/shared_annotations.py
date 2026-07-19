"""Shared annotation system with visibility + version history."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics
from engines.learning_experience_platform.collab_store import load_annotations, upsert_annotation
from engines.learning_experience_platform.permissions import can, normalize_role, require
from engines.learning_experience_platform.phase3_schemas import ANNOTATION_TYPES, ANNOTATION_VISIBILITY, SharedAnnotation


def add_shared_annotation(
    *,
    lesson_id: str,
    author_id: str,
    author_role: str,
    annotation_type: str,
    visibility: str,
    payload: dict[str, Any] | None = None,
    annotation_id: str = "",
) -> dict[str, Any]:
    role = normalize_role(author_role)
    if visibility == "private":
        if not can(role, "add_private_annotation") and role not in ("teacher", "special_educator", "administrator", "parent"):
            return require(role, "add_private_annotation")
    elif role == "student" and visibility != "private":
        return {"ok": False, "error": "students_may_only_create_private_annotations"}
    elif role == "parent" and visibility not in ("private", "parent_only", "teacher_only"):
        return {"ok": False, "error": "invalid_parent_visibility"}

    atype = annotation_type if annotation_type in ANNOTATION_TYPES else "sticky_note"
    vis = visibility if visibility in ANNOTATION_VISIBILITY else "private"
    row = SharedAnnotation(
        annotation_id=annotation_id,
        lesson_id=lesson_id,
        author_id=author_id,
        author_role=role,
        annotation_type=atype,
        visibility=vis,
        payload=dict(payload or {}),
    ).to_dict()
    saved = upsert_annotation(lesson_id, row)
    analytics.track("annotation", learner_id=author_id, lesson_id=lesson_id, payload={"type": atype, "visibility": vis})
    return {"ok": True, "annotation": saved}


def list_shared_annotations(
    lesson_id: str,
    *,
    viewer_id: str,
    viewer_role: str,
) -> dict[str, Any]:
    role = normalize_role(viewer_role)
    rows = load_annotations(lesson_id)
    visible: list[dict[str, Any]] = []
    for a in rows:
        vis = a.get("visibility") or "private"
        if a.get("author_id") == viewer_id or role == "administrator":
            visible.append(a)
        elif vis == "shared_classroom" and role in ("student", "teacher"):
            visible.append(a)
        elif vis == "teacher_only" and role in ("teacher", "administrator"):
            visible.append(a)
        elif vis == "parent_only" and role in ("parent", "teacher", "administrator"):
            visible.append(a)
        elif vis == "special_educator" and role in ("special_educator", "teacher", "administrator"):
            visible.append(a)
    return {"ok": True, "annotations": visible, "version_history_supported": True}
