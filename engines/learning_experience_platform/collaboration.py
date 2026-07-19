"""LXP Phase 3 collaboration layer — threads, mentions, announcements, receipts."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics
from engines.learning_experience_platform.collab_store import (
    append_comment,
    load_comments,
    push_notification,
    update_comment,
)
from engines.learning_experience_platform.permissions import can, filter_visible_comments, normalize_role, require
from engines.learning_experience_platform.phase3_schemas import CollaborationComment


def add_comment(
    *,
    lesson_id: str,
    author_id: str,
    author_role: str,
    body: str,
    target_type: str = "lesson",
    anchor: str = "",
    audience: str = "class",
    audience_ids: list[str] | None = None,
    parent_id: str = "",
    mentions: list[str] | None = None,
) -> dict[str, Any]:
    role = normalize_role(author_role)
    if role == "parent":
        if not can(role, "encouragement"):
            return {"ok": False, "error": "parents_cannot_comment_without_encouragement_perm"}
    elif role == "student":
        if not can(role, "reply_thread"):
            return require(role, "reply_thread")
    elif not can(role, "comment") and not can(role, "announce"):
        return require(role, "comment")

    row = CollaborationComment(
        comment_id="",
        lesson_id=lesson_id,
        author_id=author_id,
        author_role=role,
        body=body.strip(),
        target_type=target_type,
        anchor=anchor,
        audience=audience,
        audience_ids=list(audience_ids or []),
        parent_id=parent_id,
        mentions=list(mentions or []),
    ).to_dict()
    # Parents: encouragement / home notes only — never curriculum edits
    if role == "parent":
        row["kind"] = "encouragement" if not parent_id else "reply"
        row["curriculum_locked"] = True

    saved = append_comment(lesson_id, row)
    for uid in saved.get("mentions") or []:
        push_notification(uid, {"type": "mention", "lesson_id": lesson_id, "comment_id": saved["comment_id"], "from": author_id})
    analytics.track("collaboration", learner_id=author_id, lesson_id=lesson_id, payload={"action": "comment"})
    return {"ok": True, "comment": saved}


def list_comments(
    lesson_id: str,
    *,
    viewer_id: str,
    viewer_role: str,
    resolved: bool | None = None,
    target_type: str = "",
) -> dict[str, Any]:
    rows = load_comments(lesson_id)
    visible = filter_visible_comments(rows, viewer_id=viewer_id, viewer_role=viewer_role)
    if resolved is not None:
        visible = [c for c in visible if bool(c.get("resolved")) is resolved]
    if target_type:
        visible = [c for c in visible if c.get("target_type") == target_type]
    return {"ok": True, "comments": visible, "count": len(visible)}


def resolve_thread(lesson_id: str, comment_id: str, *, actor_role: str, actor_id: str) -> dict[str, Any]:
    gate = require(actor_role, "resolve_thread")
    if not gate["ok"]:
        return gate
    out = update_comment(lesson_id, comment_id, {"resolved": True, "resolved_by": actor_id})
    analytics.track("collaboration", learner_id=actor_id, lesson_id=lesson_id, payload={"action": "resolve"})
    return out


def mark_read(lesson_id: str, comment_id: str, reader_id: str) -> dict[str, Any]:
    rows = load_comments(lesson_id)
    for c in rows:
        if c.get("comment_id") == comment_id:
            read_by = list(c.get("read_by") or [])
            if reader_id not in read_by:
                read_by.append(reader_id)
            return update_comment(lesson_id, comment_id, {"read_by": read_by})
    return {"ok": False, "error": "comment_not_found"}


def announce(
    *,
    lesson_id: str,
    teacher_id: str,
    body: str,
    audience: str = "class",
    audience_ids: list[str] | None = None,
) -> dict[str, Any]:
    gate = require("teacher", "announce")
    if not gate["ok"]:
        return gate
    return add_comment(
        lesson_id=lesson_id,
        author_id=teacher_id,
        author_role="teacher",
        body=f"[Announcement] {body}",
        target_type="general",
        audience=audience,
        audience_ids=audience_ids,
    )


def threaded_view(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_parent: dict[str, list[dict[str, Any]]] = {}
    roots: list[dict[str, Any]] = []
    for c in comments:
        pid = str(c.get("parent_id") or "")
        if not pid:
            roots.append({**c, "replies": []})
        else:
            by_parent.setdefault(pid, []).append(c)
    for root in roots:
        root["replies"] = by_parent.get(root["comment_id"], [])
    return roots
