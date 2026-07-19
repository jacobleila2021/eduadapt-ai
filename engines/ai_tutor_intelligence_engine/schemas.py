"""AI Tutor Intelligence Engine schemas — grounded tutoring only."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

TUTOR_MODES = (
    "socratic",
    "guided_discovery",
    "direct_instruction",
    "worked_example",
    "step_coaching",
    "retrieval_practice",
    "spaced_review",
    "exam_prep",
    "reflection",
    "executive_function",
    "parent_explanation",
    "teacher_explanation",
)

EXPLANATION_DEPTHS = (
    "beginner",
    "developing",
    "proficient",
    "advanced",
    "expert",
)

HINT_LEVELS = (1, 2, 3, 4, 5)


@dataclass
class TutorContext:
    learner_id: str
    topic: str = ""
    grade: str = ""
    lesson_excerpt: str = ""
    concept_ids: list[str] = field(default_factory=list)
    learning_objectives: list[str] = field(default_factory=list)
    mastery_level: str = "developing"
    misconceptions: list[dict[str, Any]] = field(default_factory=list)
    accessibility_profiles: list[str] = field(default_factory=list)
    presentation_mode: str = "standard"
    reading_level: str = ""
    pathway: dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.5
    goals: list[str] = field(default_factory=list)
    teacher_mode_override: str | None = None
    allow_direct_answers: bool = True
    require_socratic: bool = False

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class GroundingPacket:
    ok: bool
    citations: list[str] = field(default_factory=list)
    rag_hits: list[dict[str, Any]] = field(default_factory=list)
    stem_artifacts: list[dict[str, Any]] = field(default_factory=list)
    official_items: list[dict[str, Any]] = field(default_factory=list)
    cie_concepts: list[dict[str, Any]] = field(default_factory=list)
    insufficient_evidence: bool = False
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class TutorTurn:
    turn_id: str
    role: str  # tutor|learner|system
    mode: str
    content: str
    grounding_ok: bool = True
    hint_level: int | None = None
    citations: list[str] = field(default_factory=list)
    explainability: str = ""

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
