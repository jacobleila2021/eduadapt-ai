"""Configurable learning workflows (teacher-configurable templates)."""

from __future__ import annotations

from typing import Any
import copy

WORKFLOW_TEMPLATES: dict[str, dict[str, Any]] = {
    "lesson_learning": {
        "name": "Lesson Learning Flow",
        "steps": [
            "lesson",
            "tutor",
            "practice",
            "reflection",
            "assessment",
            "mastery",
            "recommendation",
        ],
        "description": "Lesson → Tutor → Practice → Reflection → Assessment → Mastery → Recommendation",
    },
    "exam_revision": {
        "name": "Exam Revision Flow",
        "steps": ["revision", "quiz", "weak_areas", "tutor", "mastery_check"],
        "description": "Revision → Quiz → Weak Areas → Tutor → Mastery Check",
    },
    "homework": {
        "name": "Homework Flow",
        "steps": ["lesson", "assignment", "feedback", "parent_summary"],
        "description": "Lesson → Assignment → Feedback → Parent Summary",
    },
}

# Map workflow step → primary engine(s)
STEP_ENGINES: dict[str, list[str]] = {
    "lesson": ["curriculum", "scientific_accuracy", "accessibility"],
    "tutor": ["ai_tutor"],
    "practice": ["assessment", "adaptive_learning"],
    "reflection": ["ai_tutor", "learning_analytics"],
    "assessment": ["assessment"],
    "mastery": ["assessment", "adaptive_learning"],
    "recommendation": ["adaptive_learning", "learning_analytics"],
    "revision": ["assessment", "adaptive_learning"],
    "quiz": ["assessment"],
    "weak_areas": ["assessment", "adaptive_learning"],
    "mastery_check": ["assessment"],
    "assignment": ["assessment"],
    "feedback": ["learning_analytics", "ai_tutor"],
    "parent_summary": ["learning_analytics"],
}


class WorkflowManager:
    def __init__(self, workflow_id: str = "lesson_learning", custom: dict[str, Any] | None = None) -> None:
        if custom:
            self.template = custom
            self.workflow_id = custom.get("id") or "custom"
        else:
            self.workflow_id = workflow_id if workflow_id in WORKFLOW_TEMPLATES else "lesson_learning"
            self.template = copy.deepcopy(WORKFLOW_TEMPLATES[self.workflow_id])
        self.steps: list[str] = list(self.template.get("steps") or [])
        self.index = 0
        self.completed: list[str] = []

    def current_step(self) -> str | None:
        if 0 <= self.index < len(self.steps):
            return self.steps[self.index]
        return None

    def engines_for_current(self) -> list[str]:
        step = self.current_step()
        return list(STEP_ENGINES.get(step or "", []))

    def advance(self, *, force_step: str | None = None) -> dict[str, Any]:
        if force_step and force_step in self.steps:
            self.index = self.steps.index(force_step)
        cur = self.current_step()
        if cur:
            self.completed.append(cur)
            self.index += 1
        nxt = self.current_step()
        return {
            "completed_step": cur,
            "next_step": nxt,
            "index": self.index,
            "done": nxt is None,
            "engines_next": list(STEP_ENGINES.get(nxt or "", [])),
        }

    def configure(self, steps: list[str], *, name: str = "Custom Workflow") -> None:
        """Teacher-configurable workflow steps."""
        self.template = {"name": name, "steps": list(steps), "description": " → ".join(steps)}
        self.workflow_id = "custom"
        self.steps = list(steps)
        self.index = 0
        self.completed = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.template.get("name"),
            "description": self.template.get("description"),
            "steps": self.steps,
            "index": self.index,
            "current": self.current_step(),
            "completed": self.completed,
            "templates_available": list(WORKFLOW_TEMPLATES.keys()),
        }

    @staticmethod
    def list_templates() -> list[dict[str, Any]]:
        return [{"id": k, **v} for k, v in WORKFLOW_TEMPLATES.items()]
