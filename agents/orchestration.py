"""Named multi-agent orchestration — wraps existing engines without bypassing them."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class AgentStep:
    agent_id: str
    role: str
    status: str = "pending"  # pending | running | done | skipped | failed
    detail: str = ""
    payload: dict[str, Any] = field(default_factory=dict)


AGENT_ROSTER = (
    ("curriculum_planner", "Curriculum Planner"),
    ("lesson_analyzer", "Lesson Analyzer"),
    ("knowledge_retrieval", "Knowledge Retrieval Agent"),
    ("subject_expert", "Subject Expert"),
    ("stem_verification", "STEM Verification Agent"),
    ("accessibility", "Accessibility Specialist"),
    ("neurodiversity", "Neurodiversity Specialist"),
    ("visual_learning", "Visual Learning Agent"),
    ("assessment_designer", "Assessment Designer"),
    ("qa_agent", "QA Agent"),
    ("publishing", "Publishing Agent"),
)


class AloraOrchestrator:
    """
    Collaborative agent facade over the existing pipeline.

    Deterministic STEM and Knowledge engines remain source of truth.
    Agents here coordinate order, logging, and presentation constraints —
    they do not invent equations, graphs, or official answers.
    """

    def __init__(self, on_progress: Callable[[str, float], None] | None = None):
        self.on_progress = on_progress
        self.trace: list[AgentStep] = [
            AgentStep(agent_id=aid, role=role) for aid, role in AGENT_ROSTER
        ]

    def _emit(self, message: str, fraction: float) -> None:
        if self.on_progress:
            self.on_progress(message, fraction)

    def _mark(self, agent_id: str, status: str, detail: str = "", **payload: Any) -> None:
        for step in self.trace:
            if step.agent_id == agent_id:
                step.status = status
                step.detail = detail
                step.payload.update(payload)
                break

    def run_lesson_pipeline(self, lesson_text: str, **gen_kwargs: Any) -> dict:
        """
        Execute generate_adaptations with named agent checkpoints.
        Reuses ai_generator — does not reimplement STEM/RAG.
        """
        from ai_generator import generate_adaptations

        self._mark(
            "curriculum_planner",
            "done",
            "Uploaded source first; curriculum enrichment optional",
        )
        self._emit("Source and optional curriculum planning…", 0.02)

        def progress(msg: str, frac: float) -> None:
            low = (msg or "").lower()
            if "stem" in low or "engine" in low:
                self._mark("stem_verification", "running", msg)
                self._mark("subject_expert", "running", msg)
            elif "analyz" in low:
                self._mark("lesson_analyzer", "running", msg)
            elif "source" in low or "knowledge" in low or "retriev" in low:
                self._mark("knowledge_retrieval", "running", msg)
            elif "vocab" in low or "worksheet" in low or "exam" in low:
                self._mark("assessment_designer", "running", msg)
            elif "adapt" in low or "lesson" in low:
                self._mark("accessibility", "running", msg)
                self._mark("neurodiversity", "running", msg)
                self._mark("visual_learning", "running", msg)
            elif "done" in low:
                self._mark("qa_agent", "running", msg)
                self._mark("publishing", "running", msg)
            self._emit(msg, frac)

        result = generate_adaptations(lesson_text, on_progress=progress, **gen_kwargs)
        meta = result.get("_meta") or {}

        self._mark(
            "stem_verification",
            "done",
            f"{len(meta.get('engine_artifacts') or [])} artifacts",
            artifacts=len(meta.get("engine_artifacts") or []),
        )
        self._mark(
            "knowledge_retrieval",
            "done",
            f"{len((meta.get('knowledge') or {}).get('citations') or [])} citations",
        )
        self._mark("lesson_analyzer", "done", "context built")
        self._mark("subject_expert", "done", "engines routed")
        self._mark("accessibility", "done", "adaptations generated")
        self._mark("neurodiversity", "done", "LD / ADHD / autism variants as configured")
        self._mark("visual_learning", "done", f"{len(meta.get('preferred_visuals') or [])} visuals")
        self._mark("assessment_designer", "done", "worksheet + exam bundle")
        qa = meta.get("publish_qa") or meta.get("stem_qa") or {}
        self._mark(
            "qa_agent",
            "done" if qa.get("passed", True) else "failed",
            qa.get("blocked_reason") or "QA complete",
        )
        self._mark(
            "publishing",
            "done" if not qa.get("publish_blocked") else "failed",
            "publish gate evaluated",
        )

        result.setdefault("_meta", {})["orchestration_trace"] = [
            {
                "agent_id": s.agent_id,
                "role": s.role,
                "status": s.status,
                "detail": s.detail,
            }
            for s in self.trace
        ]
        return result
