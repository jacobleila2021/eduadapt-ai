"""Revision mode — distraction-free revision workspace (verified sources only)."""

from __future__ import annotations

from typing import Any

from engines.learning_experience_platform import analytics
from engines.learning_experience_platform.accessibility import apply_aie
from engines.learning_experience_platform.companion import companion_presence
from engines.learning_experience_platform.motivation import motivation_strip
from engines.learning_experience_platform.summary import build_summary


def revision_mode(
    *,
    learner_id: str,
    lesson: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
    exam_mode_active: bool = False,
) -> dict[str, Any]:
    context = context or {}
    lesson = lesson or {}
    outputs = context.get("engine_outputs") or {}
    cie = (outputs.get("curriculum") or {}).get("payload") or {}
    ame = (outputs.get("assessment") or {}).get("payload") or {}
    ale = (outputs.get("adaptive_learning") or {}).get("payload") or {}

    summary = build_summary(lesson, context=context)
    a11y = apply_aie(learner_id, context)

    misconceptions = []
    try:
        from engines.assessment_mastery_engine.service import api_detect_misconceptions

        text = str(lesson.get("body") or context.get("lesson_text") or "")[:2000]
        if text:
            misconceptions = (api_detect_misconceptions(text) or {}).get("misconceptions") or []
    except Exception:  # noqa: BLE001
        misconceptions = ame.get("misconceptions") or []

    guidance = {
        "source": "ATIE/CIE/AME",
        "prompts": [
            "Revisit weak competencies from AME",
            "Use verified formula sheets only",
            "Practice official exam items in Exam Mode",
        ],
        "never_invent_curriculum": True,
    }
    try:
        from engines.learning_experience_platform.tutor import tutor_panel

        guidance["tutor"] = tutor_panel({**context, "mode": "revision"})
    except Exception:  # noqa: BLE001
        pass

    companion = None if exam_mode_active else companion_presence(
        learner_id, progress_pct=50.0, context={**context, "mode": "revision"}
    )
    motivation = motivation_strip(learner_id) if not exam_mode_active else {"suppressed": True, "reason": "exam_mode"}

    analytics.track("revision", learner_id=learner_id, lesson_id=str(lesson.get("lesson_id") or ""), payload={"mode": "revision"})
    return {
        "ok": True,
        "mode": "revision",
        "distraction_free": True,
        "chapter_summaries": summary.get("key_ideas") or [],
        "concept_summaries": (summary.get("concept_map") or {}).get("concepts") or cie.get("concepts") or [],
        "learning_objectives": summary.get("learning_objectives") or cie.get("learning_objectives") or [],
        "competencies": summary.get("competencies_covered") or cie.get("competencies") or [],
        "key_vocabulary": summary.get("vocabulary_review") or [],
        "formula_sheets_ref": "use api_formula_sheets",
        "important_diagrams": summary.get("important_diagrams") or [],
        "common_misconceptions": misconceptions[:12],
        "ai_revision_guidance": guidance,
        "accessibility_recommendations": a11y,
        "adaptive_pathway": ale.get("pathway") or ale.get("learning_path") or {},
        "companion": companion,
        "motivation": motivation,
        "a11y_revision_presets": {
            "dyslexia_smart": {"font_family": "OpenDyslexic", "line_spacing": 1.8},
            "adhd_focus": {"reading_mode": "focus", "chunking": True},
            "executive_function": {"checklists": True, "timers": True},
            "ell": {"glossary_first": True, "simplified_explanations": True},
            "visual": {"diagram_priority": True},
            "auditory": {"read_along": True},
        },
        "policy": {"verified_content_only": True, "companion_suppressed_in_exam": exam_mode_active},
    }
