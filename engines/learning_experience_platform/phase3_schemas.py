"""LXP Phase 3 schemas — collaboration, workspaces, revision, assessment."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

ROLES = ("student", "teacher", "parent", "special_educator", "administrator")

ANNOTATION_VISIBILITY = (
    "private",
    "teacher_only",
    "parent_only",
    "shared_classroom",
    "special_educator",
)

ANNOTATION_TYPES = (
    "text_highlight",
    "formula_highlight",
    "diagram_highlight",
    "sticky_note",
    "voice_note",
    "drawing",
    "image",
)

COMMENT_TARGETS = ("paragraph", "diagram", "formula", "lesson", "general")
PUBLISH_AUDIENCES = ("class", "selected_students", "parents", "special_educators")

EXAM_MODES = ("practice", "timed", "review", "teacher")
FLASHCARD_KINDS = ("vocabulary", "formula", "concept", "definition", "diagram", "historical_event", "scientific_law")


# Role → allowed collaboration actions
ROLE_PERMISSIONS: dict[str, frozenset[str]] = {
    "student": frozenset({
        "read_lesson", "add_private_annotation", "reply_thread", "use_revision",
        "use_flashcards", "use_exam_practice", "view_own_progress",
    }),
    "teacher": frozenset({
        "read_lesson", "comment", "highlight", "pin_explanation", "teaching_notes",
        "revision_notes", "attach_resources", "approve_adaptation", "lock_section",
        "assign_activity", "schedule_revision", "create_checkpoint", "discussion_prompt",
        "track_completion", "track_tutor", "track_revision", "view_a11y", "compare_adaptations",
        "publish_comment", "announce", "resolve_thread", "view_class_progress",
        "exam_teacher_mode", "moderate",
    }),
    "parent": frozenset({
        "view_learner_progress", "view_teacher_comments", "encouragement",
        "home_learning_notes", "mark_practice", "view_a11y", "view_revision_planner",
        "view_achievements", "view_reading_habits",
    }),
    "special_educator": frozenset({
        "view_a11y", "accommodation_recs", "ef_supports", "intervention_plan",
        "reading_supports", "observations", "progress_monitor", "iep_notes",
        "therapy_notes", "accommodation_history", "goal_tracking", "comment",
        "collaborate_teacher_parent",
    }),
    "administrator": frozenset({"*"}),
}


@dataclass
class CollaborationComment:
    comment_id: str
    lesson_id: str
    author_id: str
    author_role: str
    body: str
    target_type: str = "lesson"
    anchor: str = ""
    audience: str = "class"
    audience_ids: list[str] = field(default_factory=list)
    parent_id: str = ""
    mentions: list[str] = field(default_factory=list)
    resolved: bool = False
    read_by: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SharedAnnotation:
    annotation_id: str
    lesson_id: str
    author_id: str
    author_role: str
    annotation_type: str
    visibility: str
    payload: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    history: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
