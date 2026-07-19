"""LXP intelligence aggregator — Phase 1 layout + Phase 2 intelligence bundle."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics
from engines.learning_experience_platform.accessibility import apply_aie
from engines.learning_experience_platform.ai_explain import paragraph_actions
from engines.learning_experience_platform.companion import companion_presence
from engines.learning_experience_platform.glossary import build_glossary
from engines.learning_experience_platform.layout import build_layout
from engines.learning_experience_platform.motivation import motivation_strip
from engines.learning_experience_platform.progress import estimate_reading_minutes, update_progress
from engines.learning_experience_platform.read_along import read_along_bundle
from engines.learning_experience_platform.session_store import load_preferences, load_progress
from engines.learning_experience_platform.stem import stem_interactives
from engines.learning_experience_platform.summary import build_summary
from engines.learning_experience_platform.tutor import tutor_panel
from engines.learning_experience_platform.voice import voice_controls


def analyze_lxp_context(context: dict[str, Any]) -> dict[str, Any]:
    learner_id = str(context.get("learner_id") or context.get("user_id") or "anonymous")
    lesson = context.get("lesson") or {}
    if not lesson and context.get("lesson_text"):
        lesson = {
            "title": context.get("topic") or "Lesson",
            "body": context.get("lesson_text"),
            "sections": [{"id": "sec_0", "title": "Reading", "body": context.get("lesson_text"), "anchor": "sec_0"}],
        }
    lesson_id = str(lesson.get("lesson_id") or context.get("lesson_id") or lesson.get("title") or "lesson")
    lesson_text = str(lesson.get("body") or context.get("lesson_text") or "")

    a11y = apply_aie(learner_id, context)
    prefs = a11y.get("preferences") or load_preferences(learner_id)
    progress = load_progress(learner_id, lesson_id)
    if not progress.get("estimated_minutes"):
        update_progress(learner_id, lesson_id, lesson_text=lesson_text, reading_pct=float(progress.get("reading_pct") or 0))
        progress = load_progress(learner_id, lesson_id)

    layout = build_layout(
        lesson,
        prefs=prefs,
        progress=progress,
        meta={
            "board": context.get("board"),
            "grade": context.get("grade"),
            "subject": context.get("subject"),
            "chapter": context.get("chapter"),
            "topic": context.get("topic") or lesson.get("title"),
        },
    )

    sections = lesson.get("sections") or []
    first_body = ""
    if sections and isinstance(sections[0], dict):
        first_body = str(sections[0].get("body") or "")
    paragraph = str(context.get("paragraph") or first_body or lesson_text[:400])
    phase2 = {
        "ai_explain": paragraph_actions(paragraph, context=context) if paragraph else {},
        "read_along": read_along_bundle(lesson_text, prefs=prefs),
        "stem": stem_interactives(context),
        "glossary": build_glossary(context=context),
        "summary": build_summary(lesson, context=context),
        "tutor": tutor_panel({**context, "paragraph": paragraph}),
        "companion": companion_presence(learner_id, progress_pct=float(progress.get("reading_pct") or 0), context=context),
        "motivation": motivation_strip(learner_id),
        "voice": voice_controls(),
    }

    phase3 = None
    if context.get("include_phase3", True):
        from engines.learning_experience_platform.phase3 import build_phase3

        phase3 = build_phase3({**context, "lesson": lesson, "learner_id": learner_id, "lesson_id": lesson_id})

    phase4 = None
    if context.get("include_phase4", True):
        from engines.learning_experience_platform.phase4 import build_phase4

        phase4 = build_phase4({**context, "learner_id": learner_id, "lesson_id": lesson_id})

    analytics.track("lxp_session_plan", learner_id=learner_id, lesson_id=lesson_id, payload={"phase": "1+2+3+4"})

    return {
        "system": "LXP",
        "phases": [
            "phase1_core_reader",
            "phase2_interactive_intelligence",
            "phase3_collab_revision_assessment",
            "phase4_premium_experience",
        ],
        "learner_id": learner_id,
        "lesson_id": lesson_id,
        "layout": layout,
        "preferences": prefs,
        "progress": progress,
        "accessibility": a11y,
        "estimated_reading_minutes": estimate_reading_minutes(lesson_text),
        "phase2": phase2,
        "phase3": phase3,
        "phase4": phase4,
        "analytics": analytics.summary(learner_id, lesson_id),
        "performance": (phase4 or {}).get("performance") or {
            "lazy_loading": True,
            "diagram_caching": True,
            "offline_caching": True,
            "smooth_scrolling": True,
        },
        "policy": {
            "never_generate_curriculum": True,
            "engines_consumed_not_replaced": True,
            "verified_content_only": True,
            "parents_never_alter_curriculum": True,
            "never_auto_translate_curriculum": True,
            "never_delay_learning_content": True,
        },
    }
