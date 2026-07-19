"""UI service — routes Phase 3 panels into the unified LXP workspace."""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.learning_experience_platform.collaboration import render_collaboration
from ui.learning_experience_platform.dashboards import render_role_dashboard
from ui.learning_experience_platform.exam_mode import render_exam_mode
from ui.learning_experience_platform.flashcards import render_flashcards
from ui.learning_experience_platform.formula_sheets import render_formula_sheets
from ui.learning_experience_platform.parent_workspace import render_parent_workspace
from ui.learning_experience_platform.revision_mode import render_revision_mode
from ui.learning_experience_platform.revision_planner import render_revision_planner
from ui.learning_experience_platform.special_educator_workspace import render_special_educator_workspace
from ui.learning_experience_platform.teacher_workspace import render_teacher_workspace


def render_phase3_panel(
    *,
    learner_id: str,
    lesson_id: str,
    lesson: dict[str, Any] | None = None,
    topic: str = "",
    role: str = "student",
    context: dict[str, Any] | None = None,
) -> None:
    """Tabbed Phase 3 experience inside the LXP reader."""
    context = context or {}
    role = (role or "student").lower()
    tabs = st.tabs([
        "Revision",
        "Flashcards",
        "Formulae",
        "Exam",
        "Planner",
        "Collaborate",
        "Workspace",
    ])
    with tabs[0]:
        render_revision_mode(learner_id=learner_id, lesson=lesson, context=context)
    with tabs[1]:
        render_flashcards(learner_id=learner_id, lesson=lesson, context=context)
    with tabs[2]:
        render_formula_sheets(subject=str(context.get("subject") or ""), lesson=lesson, context=context)
    with tabs[3]:
        render_exam_mode(learner_id=learner_id, topic=topic, lesson_text=str((lesson or {}).get("body") or ""), context=context)
    with tabs[4]:
        render_revision_planner(learner_id=learner_id, topic=topic, context=context)
    with tabs[5]:
        render_collaboration(lesson_id=lesson_id, user_id=learner_id, role=role)
    with tabs[6]:
        render_role_dashboard(role=role, user_id=learner_id, learner_id=learner_id, lesson_id=lesson_id, context=context)
        if role == "teacher":
            render_teacher_workspace(teacher_id=learner_id, lesson_id=lesson_id, context=context)
        elif role == "parent":
            render_parent_workspace(parent_id=learner_id, learner_id=str(context.get("child_id") or learner_id), lesson_id=lesson_id, context=context)
        elif role in ("special_educator", "sped"):
            render_special_educator_workspace(educator_id=learner_id, learner_id=str(context.get("child_id") or learner_id), lesson_id=lesson_id, context=context)
