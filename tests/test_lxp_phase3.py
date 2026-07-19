"""LXP Phase 3 — collaboration, workspaces, revision & assessment."""

from __future__ import annotations

import uuid

from engines.learning_experience_platform import LearningExperienceEngine
from engines.learning_experience_platform.permissions import can, filter_visible_comments, normalize_role
from engines.learning_experience_platform.service import (
    api_add_comment,
    api_exam_mode,
    api_flashcards,
    api_formula_sheets,
    api_list_comments,
    api_parent_workspace,
    api_phase3,
    api_resolve_comment,
    api_revision_mode,
    api_revision_planner,
    api_shared_annotation,
    api_special_educator_workspace,
    api_teacher_workspace,
)
from engines.verified_learning_engine import reset_registry


def test_rbac_roles():
    assert can("teacher", "announce")
    assert can("parent", "encouragement")
    assert not can("parent", "lock_section")
    assert can("special_educator", "iep_notes") or can("special_educator", "view_a11y")
    assert normalize_role("sped") == "special_educator"


def test_comment_permissions_and_visibility():
    lesson = f"lesson_p3_{uuid.uuid4().hex[:8]}"
    teacher = f"t_{uuid.uuid4().hex[:6]}"
    student = f"s_{uuid.uuid4().hex[:6]}"
    parent = f"p_{uuid.uuid4().hex[:6]}"

    t = api_add_comment(
        lesson_id=lesson,
        author_id=teacher,
        author_role="teacher",
        body="Review chloroplast section",
        target_type="paragraph",
        audience="class",
    )
    assert t["ok"]
    p = api_add_comment(
        lesson_id=lesson,
        author_id=parent,
        author_role="parent",
        body="Proud of your effort!",
        audience="selected_students",
        audience_ids=[student],
    )
    assert p["ok"]
    assert p["comment"].get("curriculum_locked") is True

    visible_student = api_list_comments(lesson_id=lesson, viewer_id=student, viewer_role="student")
    assert any(c.get("author_id") == teacher for c in visible_student["comments"])

    # Parent-only audience filtered from student class feed when audience=parents
    api_add_comment(
        lesson_id=lesson,
        author_id=teacher,
        author_role="teacher",
        body="For parents: reading goal",
        audience="parents",
    )
    filtered = filter_visible_comments(
        api_list_comments(lesson_id=lesson, viewer_id=teacher, viewer_role="teacher")["comments"],
        viewer_id=student,
        viewer_role="student",
    )
    assert all(c.get("audience") != "parents" for c in filtered)

    resolved = api_resolve_comment(
        lesson_id=lesson,
        comment_id=t["comment"]["comment_id"],
        actor_role="teacher",
        actor_id=teacher,
    )
    assert resolved.get("ok")


def test_shared_annotation_version_history():
    lesson = f"ann_{uuid.uuid4().hex[:8]}"
    teacher = f"t_{uuid.uuid4().hex[:6]}"
    a1 = api_shared_annotation(
        lesson_id=lesson,
        author_id=teacher,
        author_role="teacher",
        annotation_type="formula_highlight",
        visibility="shared_classroom",
        payload={"text": "F=ma"},
    )
    assert a1["ok"]
    aid = a1["annotation"]["annotation_id"]
    a2 = api_shared_annotation(
        lesson_id=lesson,
        author_id=teacher,
        author_role="teacher",
        annotation_type="formula_highlight",
        visibility="shared_classroom",
        payload={"text": "F=ma (verified)"},
        annotation_id=aid,
    )
    assert a2["annotation"]["version"] >= 2
    assert a2["annotation"]["history"]


def test_student_cannot_create_classroom_annotation():
    out = api_shared_annotation(
        lesson_id="L1",
        author_id="s1",
        author_role="student",
        annotation_type="sticky_note",
        visibility="shared_classroom",
        payload={"text": "x"},
    )
    assert out.get("ok") is False


def test_workspaces():
    lesson = f"ws_{uuid.uuid4().hex[:6]}"
    tw = api_teacher_workspace(teacher_id="teacher1", lesson_id=lesson, learner_ids=["s1", "s2"])
    assert tw["ok"] and tw["workspace"] == "teacher"
    pw = api_parent_workspace(parent_id="parent1", learner_id="s1", lesson_id=lesson)
    assert pw["ok"] and pw["policy"]["never_alter_curriculum"] is True
    sw = api_special_educator_workspace(educator_id="sped1", learner_id="s1", lesson_id=lesson)
    assert sw["ok"] and sw["policy"]["never_alter_curriculum"] is True


def test_revision_flashcards_formulae_exam_planner():
    learner = f"rev_{uuid.uuid4().hex[:6]}"
    lesson = {
        "lesson_id": "cells",
        "title": "Cell Structure",
        "body": "Plant cells have chloroplasts.",
        "word_wall": [{"term": "chloroplast", "definition": "Organelle that captures light"}],
        "learning_objectives": ["Identify cell organelles"],
    }
    context = {
        "engine_outputs": {
            "scientific_accuracy": {
                "payload": {
                    "artifacts": [
                        {"kind": "formula", "payload": {"name": "Force", "latex": "F=ma", "variables": ["F", "m", "a"]}}
                    ]
                }
            },
            "curriculum": {"payload": {"concepts": [{"title": "Force", "definition": "A push or a pull"}]}},
        }
    }
    rev = api_revision_mode(learner_id=learner, lesson=lesson, context=context)
    assert rev["ok"] and rev["distraction_free"]
    cards = api_flashcards(learner_id=learner, lesson=lesson, context=context)
    assert cards["ok"] and cards["count"] >= 1 and cards["policy"]["never_invent_cards"]
    sheets = api_formula_sheets(subject="physics", lesson=lesson, context=context)
    assert sheets["ok"] and sheets["policy"]["never_invent_formulas"]
    assert any(f["formula"] == "F=ma" for f in sheets["formulae"])
    exam = api_exam_mode(learner_id=learner, topic="Cell", lesson_text=lesson["body"], mode="practice", context=context)
    assert exam["ok"] and exam["companion_suppressed"] is True
    assert exam["policy"]["official_answers_from_verified_banks_only"]
    plan = api_revision_planner(learner_id=learner, exam_days=10, topic="Cell", context=context)
    assert plan["ok"] and plan["schedule"]


def test_phase3_bundle_and_engine():
    eng = LearningExperienceEngine()
    out = eng.process(
        {
            "learner_id": f"p3_{uuid.uuid4().hex[:6]}",
            "role": "teacher",
            "lesson_text": "Force is a push or a pull.",
            "topic": "Force",
            "include_phase3": True,
            "word_wall": [{"term": "force", "definition": "Push or pull"}],
        }
    )
    assert out.ok
    assert "phase3_collab_revision_assessment" in out.payload["phases"]
    assert out.payload.get("phase3")
    assert out.payload["phase3"]["policy"]["parents_never_alter_curriculum"]

    bundle = api_phase3(
        learner_id=f"b_{uuid.uuid4().hex[:6]}",
        role="student",
        lesson={"title": "Cells", "body": "Cells are units of life.", "word_wall": [{"term": "cell", "definition": "Basic unit"}]},
        topic="Cells",
    )
    assert bundle["ok"]
    assert bundle["flashcards"]["ok"]
    assert bundle["exam_mode"]["companion_suppressed"]


def test_legacy_phase1_2_regression():
    reg = reset_registry()
    assert reg.get("learning_experience").health_check().ok
    assert "phases=1+2+3+4" in (reg.get("learning_experience").health_check().detail or "")


def test_lxp_phase3_collab_revision_smoke(capsys):
    """LXP_PHASE3_COLLAB_REVISION_SMOKE_OK"""
    learner = f"smoke_p3_{uuid.uuid4().hex[:8]}"
    lesson_id = f"smoke_lesson_{uuid.uuid4().hex[:6]}"
    assert api_teacher_workspace(teacher_id="t_smoke", lesson_id=lesson_id, learner_ids=[learner])["ok"]
    assert api_parent_workspace(parent_id="p_smoke", learner_id=learner, lesson_id=lesson_id)["ok"]
    assert api_special_educator_workspace(educator_id="e_smoke", learner_id=learner, lesson_id=lesson_id)["ok"]
    assert api_add_comment(
        lesson_id=lesson_id,
        author_id="t_smoke",
        author_role="teacher",
        body="Checkpoint tomorrow",
        audience="class",
    )["ok"]
    lesson = {
        "lesson_id": lesson_id,
        "body": "Photosynthesis occurs in chloroplasts.",
        "word_wall": [{"term": "photosynthesis", "definition": "Making food using light"}],
    }
    assert api_revision_mode(learner_id=learner, lesson=lesson)["ok"]
    assert api_flashcards(learner_id=learner, lesson=lesson)["ok"]
    assert api_exam_mode(learner_id=learner, topic="Photosynthesis", mode="practice")["ok"]
    assert api_revision_planner(learner_id=learner, exam_days=7, topic="Photosynthesis")["ok"]
    eng = LearningExperienceEngine()
    assert eng.process({"learner_id": learner, "lesson_text": lesson["body"], "topic": "Photosynthesis"}).ok

    with capsys.disabled():
        print("LXP_PHASE3_COLLAB_REVISION_SMOKE_OK")
