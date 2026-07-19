"""REST-shaped API facade for LXP Phases 1–2."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics
from engines.learning_experience_platform.accessibility import apply_aie
from engines.learning_experience_platform.ai_explain import paragraph_actions
from engines.learning_experience_platform.click_explain import explain_target
from engines.learning_experience_platform.contextual_chat import build_chat_context, chat_turn
from engines.learning_experience_platform.glossary import build_glossary
from engines.learning_experience_platform.intelligence import analyze_lxp_context
from engines.learning_experience_platform.layout import build_layout
from engines.learning_experience_platform.offline import cache_lesson, sync_cache
from engines.learning_experience_platform.progress import update_progress
from engines.learning_experience_platform.read_along import read_along_bundle
from engines.learning_experience_platform.search import search_all
from engines.learning_experience_platform.session_store import (
    add_bookmark,
    add_highlight,
    delete_bookmark,
    delete_highlight,
    delete_note,
    list_bookmarks,
    list_highlights,
    list_notes,
    load_preferences,
    save_preferences,
    upsert_note,
)
from engines.learning_experience_platform.stem import stem_interactives
from engines.learning_experience_platform.summary import build_summary
from engines.learning_experience_platform.themes import resolve_theme


def api_open_reader(**kwargs: Any) -> dict[str, Any]:
    return {"ok": True, **analyze_lxp_context(kwargs)}


def api_update_preferences(learner_id: str, prefs: dict[str, Any]) -> dict[str, Any]:
    return {"ok": True, "preferences": save_preferences(learner_id, prefs)}


def api_get_preferences(learner_id: str) -> dict[str, Any]:
    return {"ok": True, "preferences": load_preferences(learner_id), "theme": resolve_theme(load_preferences(learner_id).get("theme") or "light")}


def api_update_progress(learner_id: str, lesson_id: str, **kwargs: Any) -> dict[str, Any]:
    out = update_progress(learner_id, lesson_id, **{k: kwargs[k] for k in kwargs if k in (
        "reading_pct", "delta_seconds", "resume_offset", "resume_anchor", "lesson_text"
    )})
    analytics.track("reading_time", learner_id=learner_id, lesson_id=lesson_id, payload=out.get("progress"))
    return out


def api_add_note(learner_id: str, **note: Any) -> dict[str, Any]:
    row = upsert_note(learner_id, note)
    analytics.track("note", learner_id=learner_id, lesson_id=str(note.get("lesson_id") or ""), payload=row)
    return {"ok": True, "note": row}


def api_list_notes(learner_id: str, lesson_id: str = "") -> dict[str, Any]:
    return {"ok": True, "notes": list_notes(learner_id, lesson_id)}


def api_delete_note(learner_id: str, note_id: str) -> dict[str, Any]:
    return delete_note(learner_id, note_id)


def api_add_highlight(learner_id: str, **highlight: Any) -> dict[str, Any]:
    row = add_highlight(learner_id, highlight)
    analytics.track("highlight", learner_id=learner_id, lesson_id=str(highlight.get("lesson_id") or ""), payload=row)
    return {"ok": True, "highlight": row}


def api_list_highlights(learner_id: str, lesson_id: str = "") -> dict[str, Any]:
    return {"ok": True, "highlights": list_highlights(learner_id, lesson_id)}


def api_delete_highlight(learner_id: str, highlight_id: str) -> dict[str, Any]:
    return delete_highlight(learner_id, highlight_id)


def api_add_bookmark(learner_id: str, **bookmark: Any) -> dict[str, Any]:
    row = add_bookmark(learner_id, bookmark)
    analytics.track("bookmark", learner_id=learner_id, lesson_id=str(bookmark.get("lesson_id") or ""), payload=row)
    return {"ok": True, "bookmark": row}


def api_list_bookmarks(learner_id: str, folder: str = "") -> dict[str, Any]:
    return {"ok": True, "bookmarks": list_bookmarks(learner_id, folder)}


def api_delete_bookmark(learner_id: str, bookmark_id: str) -> dict[str, Any]:
    return delete_bookmark(learner_id, bookmark_id)


def api_search(**kwargs: Any) -> dict[str, Any]:
    return search_all(**{k: kwargs[k] for k in ("learner_id", "query", "lesson_text", "glossary", "scope") if k in kwargs})


def api_offline_cache(**kwargs: Any) -> dict[str, Any]:
    out = cache_lesson(**{k: kwargs[k] for k in kwargs if k in (
        "learner_id", "lesson_id", "lesson_payload", "notes", "bookmarks", "highlights", "progress", "audio_meta"
    )})
    analytics.track("offline", learner_id=str(kwargs.get("learner_id") or ""), lesson_id=str(kwargs.get("lesson_id") or ""), payload=out)
    return out


def api_offline_sync(cache_id: str, **kwargs: Any) -> dict[str, Any]:
    return sync_cache(cache_id, server_progress=kwargs.get("server_progress"))


def api_explain_paragraph(paragraph: str, **kwargs: Any) -> dict[str, Any]:
    out = paragraph_actions(paragraph, context=kwargs.get("context"))
    analytics.track("ai_explain", learner_id=str(kwargs.get("learner_id") or ""), payload={"actions": list((out.get("actions") or {}).keys())})
    return out


def api_chat(message: str, **kwargs: Any) -> dict[str, Any]:
    ctx = build_chat_context(
        lesson=kwargs.get("lesson"),
        paragraph=str(kwargs.get("paragraph") or ""),
        competency=str(kwargs.get("competency") or ""),
        learner_id=str(kwargs.get("learner_id") or ""),
        engine_outputs=kwargs.get("engine_outputs"),
        conversation=kwargs.get("conversation"),
    )
    out = chat_turn(message, ctx)
    analytics.track("chat", learner_id=str(kwargs.get("learner_id") or ""), payload={"retained": True})
    return out


def api_click_explain(target: str, **kwargs: Any) -> dict[str, Any]:
    return explain_target(target, target_type=str(kwargs.get("target_type") or "concept"), context=kwargs.get("context"))


def api_glossary(**kwargs: Any) -> dict[str, Any]:
    out = build_glossary(kwargs.get("terms"), context=kwargs.get("context"))
    analytics.track("glossary", learner_id=str(kwargs.get("learner_id") or ""))
    return out


def api_read_along(lesson_text: str, **kwargs: Any) -> dict[str, Any]:
    out = read_along_bundle(lesson_text, prefs=kwargs.get("prefs"))
    analytics.track("read_along", learner_id=str(kwargs.get("learner_id") or ""))
    return out


def api_stem(**kwargs: Any) -> dict[str, Any]:
    out = stem_interactives(kwargs.get("context"))
    analytics.track("stem", learner_id=str(kwargs.get("learner_id") or ""))
    return out


def api_summary(**kwargs: Any) -> dict[str, Any]:
    return build_summary(kwargs.get("lesson"), context=kwargs.get("context"))


def api_apply_accessibility(learner_id: str, **kwargs: Any) -> dict[str, Any]:
    out = apply_aie(learner_id, kwargs.get("context"))
    analytics.track("accessibility", learner_id=learner_id)
    return out


def api_layout(**kwargs: Any) -> dict[str, Any]:
    return {"ok": True, "layout": build_layout(kwargs.get("lesson"), prefs=kwargs.get("prefs"), progress=kwargs.get("progress"), meta=kwargs.get("meta"))}


def api_analytics(learner_id: str = "", lesson_id: str = "") -> dict[str, Any]:
    return {"ok": True, "analytics": analytics.summary(learner_id, lesson_id)}


# --- Phase 3: collaboration, workspaces, revision & assessment ---


def api_add_comment(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.collaboration import add_comment

    return add_comment(**{k: kwargs[k] for k in kwargs if k in (
        "lesson_id", "author_id", "author_role", "body", "target_type", "anchor",
        "audience", "audience_ids", "parent_id", "mentions",
    )})


def api_list_comments(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.collaboration import list_comments, threaded_view

    out = list_comments(
        str(kwargs.get("lesson_id") or ""),
        viewer_id=str(kwargs.get("viewer_id") or ""),
        viewer_role=str(kwargs.get("viewer_role") or "student"),
        resolved=kwargs.get("resolved"),
        target_type=str(kwargs.get("target_type") or ""),
    )
    if kwargs.get("threaded"):
        out["threads"] = threaded_view(out.get("comments") or [])
    return out


def api_resolve_comment(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.collaboration import resolve_thread

    return resolve_thread(
        str(kwargs.get("lesson_id") or ""),
        str(kwargs.get("comment_id") or ""),
        actor_role=str(kwargs.get("actor_role") or "teacher"),
        actor_id=str(kwargs.get("actor_id") or ""),
    )


def api_announce(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.collaboration import announce

    return announce(
        lesson_id=str(kwargs.get("lesson_id") or ""),
        teacher_id=str(kwargs.get("teacher_id") or ""),
        body=str(kwargs.get("body") or ""),
        audience=str(kwargs.get("audience") or "class"),
        audience_ids=kwargs.get("audience_ids"),
    )


def api_shared_annotation(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.shared_annotations import add_shared_annotation

    return add_shared_annotation(**{k: kwargs[k] for k in kwargs if k in (
        "lesson_id", "author_id", "author_role", "annotation_type", "visibility", "payload", "annotation_id",
    )})


def api_list_shared_annotations(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.shared_annotations import list_shared_annotations

    return list_shared_annotations(
        str(kwargs.get("lesson_id") or ""),
        viewer_id=str(kwargs.get("viewer_id") or ""),
        viewer_role=str(kwargs.get("viewer_role") or "student"),
    )


def api_notifications(user_id: str) -> dict[str, Any]:
    from engines.learning_experience_platform.notifications import api_list_notifications

    return api_list_notifications(user_id)


def api_teacher_workspace(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.teacher_workspace import teacher_workspace

    return teacher_workspace(
        teacher_id=str(kwargs.get("teacher_id") or ""),
        lesson_id=str(kwargs.get("lesson_id") or ""),
        learner_ids=kwargs.get("learner_ids"),
        context=kwargs.get("context"),
    )


def api_parent_workspace(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.parent_workspace import parent_workspace

    return parent_workspace(
        parent_id=str(kwargs.get("parent_id") or ""),
        learner_id=str(kwargs.get("learner_id") or ""),
        lesson_id=str(kwargs.get("lesson_id") or ""),
        context=kwargs.get("context"),
    )


def api_special_educator_workspace(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.special_educator_workspace import special_educator_workspace

    return special_educator_workspace(
        educator_id=str(kwargs.get("educator_id") or ""),
        learner_id=str(kwargs.get("learner_id") or ""),
        lesson_id=str(kwargs.get("lesson_id") or ""),
        context=kwargs.get("context"),
    )


def api_revision_mode(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.revision_mode import revision_mode

    return revision_mode(
        learner_id=str(kwargs.get("learner_id") or "anonymous"),
        lesson=kwargs.get("lesson"),
        context=kwargs.get("context"),
        exam_mode_active=bool(kwargs.get("exam_mode_active")),
    )


def api_flashcards(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.flashcards import build_flashcards

    return build_flashcards(
        lesson=kwargs.get("lesson"),
        context=kwargs.get("context"),
        learner_id=str(kwargs.get("learner_id") or ""),
    )


def api_formula_sheets(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.formula_sheets import build_formula_sheets

    return build_formula_sheets(
        subject=str(kwargs.get("subject") or ""),
        context=kwargs.get("context"),
        lesson=kwargs.get("lesson"),
    )


def api_exam_mode(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.exam_mode import exam_mode

    return exam_mode(
        learner_id=str(kwargs.get("learner_id") or "anonymous"),
        topic=str(kwargs.get("topic") or ""),
        lesson_text=str(kwargs.get("lesson_text") or ""),
        mode=str(kwargs.get("mode") or "practice"),
        context=kwargs.get("context"),
        timed_seconds=kwargs.get("timed_seconds"),
    )


def api_official_exam(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.exam_mode import official_exam_bundle

    return official_exam_bundle(topic=str(kwargs.get("topic") or ""), learner_id=str(kwargs.get("learner_id") or ""))


def api_revision_planner(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.revision_planner import revision_planner

    return revision_planner(
        learner_id=str(kwargs.get("learner_id") or "anonymous"),
        exam_date=str(kwargs.get("exam_date") or ""),
        exam_days=kwargs.get("exam_days"),
        available_minutes_per_day=int(kwargs.get("available_minutes_per_day") or 45),
        topic=str(kwargs.get("topic") or ""),
        lesson_text=str(kwargs.get("lesson_text") or ""),
        context=kwargs.get("context"),
    )


def api_ai_revision(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.ai_revision import ai_revision_assist

    return ai_revision_assist(
        learner_id=str(kwargs.get("learner_id") or "anonymous"),
        message=str(kwargs.get("message") or ""),
        action=str(kwargs.get("action") or "explain"),
        context=kwargs.get("context"),
    )


def api_workspace_dashboard(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.dashboards import workspace_dashboard

    return workspace_dashboard(
        str(kwargs.get("role") or "student"),
        user_id=str(kwargs.get("user_id") or ""),
        learner_id=str(kwargs.get("learner_id") or ""),
        lesson_id=str(kwargs.get("lesson_id") or ""),
        learner_ids=kwargs.get("learner_ids"),
        context=kwargs.get("context"),
    )


def api_phase3(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.phase3 import build_phase3

    return {"ok": True, **build_phase3(kwargs)}


# --- Phase 4: premium experience, performance & polish ---


def api_phase4(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.phase4 import build_phase4

    return {"ok": True, **build_phase4(kwargs)}


def api_premium_settings(learner_id: str, patch: dict[str, Any] | None = None) -> dict[str, Any]:
    from engines.learning_experience_platform.phase4_settings import load_premium_settings, save_premium_settings

    if patch:
        return save_premium_settings(learner_id, patch)
    return {"ok": True, "settings": load_premium_settings(learner_id)}


def api_offline_package(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.phase4_offline import build_full_package

    return build_full_package(**{k: kwargs[k] for k in kwargs if k in (
        "learner_id", "lesson_id", "lesson_payload", "notes", "highlights", "bookmarks",
        "comments", "flashcards", "revision_plan", "voice", "glossary", "companion_memory",
        "preferences", "progress",
    )})


def api_sync_status(learner_id: str = "") -> dict[str, Any]:
    from engines.learning_experience_platform.phase4_offline import sync_status

    return sync_status(learner_id)


def api_background_sync(learner_id: str = "") -> dict[str, Any]:
    from engines.learning_experience_platform.phase4_offline import background_sync

    return background_sync(learner_id)


def api_enqueue_delta(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.phase4_offline import enqueue_delta

    return enqueue_delta(
        str(kwargs.get("learner_id") or ""),
        str(kwargs.get("entity") or "note"),
        str(kwargs.get("entity_id") or ""),
        str(kwargs.get("op") or "upsert"),
        dict(kwargs.get("payload") or {}),
    )


def api_resolve_sync_conflict(**kwargs: Any) -> dict[str, Any]:
    from engines.learning_experience_platform.phase4_offline import detect_conflict, resolve_conflict

    local = dict(kwargs.get("local") or {})
    remote = dict(kwargs.get("remote") or {})
    detected = detect_conflict(local, remote)
    if not detected.get("conflict"):
        return {"ok": True, "conflict": False, "resolved": local or remote}
    return resolve_conflict(local, remote, strategy=str(kwargs.get("strategy") or "merge_by_timestamp"))


def api_experience_analytics(learner_id: str = "") -> dict[str, Any]:
    from engines.learning_experience_platform.phase4_analytics import experience_summary

    return experience_summary(learner_id)
