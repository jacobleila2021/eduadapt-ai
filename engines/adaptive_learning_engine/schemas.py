"""Adaptive Learning Engine schemas — decision layer (no content generation)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DIFFICULTY_LEVELS = (
    "foundation",
    "guided",
    "standard",
    "advanced",
    "extension",
    "challenge",
)

PATHWAY_TYPES = (
    "linear",
    "competency_based",
    "prerequisite",
    "spiral",
    "mastery",
    "adaptive_review",
    "enrichment",
    "remediation",
)

REVIEW_INTERVALS_DAYS = (0, 1, 3, 7, 14, 30, 60)


@dataclass
class LearnerModel:
    learner_id: str
    grade: str = ""
    curriculum: str = ""
    subjects: list[str] = field(default_factory=list)
    concepts_mastered: list[str] = field(default_factory=list)
    concepts_developing: list[str] = field(default_factory=list)
    concepts_at_risk: list[str] = field(default_factory=list)
    reading_level: str = ""
    working_memory: str = ""
    processing_speed: str = ""
    attention: str = ""
    accessibility_profiles: list[str] = field(default_factory=list)
    preferred_modalities: list[str] = field(default_factory=list)
    motivation_level: float = 0.5
    confidence: float = 0.5
    time_on_task_min: float = 0.0
    completion_rate: float = 0.0
    assessment_history: list[dict[str, Any]] = field(default_factory=list)
    revision_history: list[dict[str, Any]] = field(default_factory=list)
    learning_streak: int = 0
    intervention_history: list[dict[str, Any]] = field(default_factory=list)
    teacher_observations: list[str] = field(default_factory=list)
    parent_observations: list[str] = field(default_factory=list)
    teacher_overrides: list[dict[str, Any]] = field(default_factory=list)
    updated_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LearnerModel":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        return cls(**{k: v for k, v in data.items() if k in known})


@dataclass
class ExplainableDecision:
    """Teacher Override & Explainability Layer — every adaptive choice is auditable."""

    decision_id: str
    decision_type: str
    choice: str
    explanation: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.8
    teacher_override_allowed: bool = True
    overridden_by: str | None = None
    override_reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class PathwayStep:
    step_id: str
    concept_id: str
    title: str = ""
    activity_type: str = "lesson"  # lesson|practice|review|intervention|enrichment|assessment
    difficulty: str = "standard"
    presentation_mode: str = "standard"
    rationale: str = ""
    prerequisites_ok: bool = True
    estimated_minutes: int = 15

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
