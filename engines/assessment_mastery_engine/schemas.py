"""Assessment & Mastery Engine schemas — evidence-based learner model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Prompt #16 mastery ladder (extends CIE progression with approaching_proficiency)
MASTERY_LEVELS = (
    "beginning",
    "developing",
    "approaching_proficiency",
    "proficient",
    "advanced",
    "mastered",
)

ASSESSMENT_TYPES = (
    "diagnostic",
    "formative",
    "summative",
    "competency",
    "adaptive",
    "practice",
)

EVIDENCE_SOURCES = (
    "assessment",
    "assignment",
    "practice",
    "project",
    "teacher_observation",
    "ai_tutor",
    "reflection",
    "worksheet",
    "official_exam_practice",
)

ITEM_TYPES = (
    "mcq",
    "short_answer",
    "long_answer",
    "case_study",
    "project",
    "practical",
    "assertion_reason",
    "diagram",
    "hots",
    "competency",
)


@dataclass
class AssessmentItemRef:
    """Pointer into official bank / KIE — never invents answers."""

    item_id: str
    question_type: str = "mcq"
    concept_id: str = ""
    learning_outcome_id: str = ""
    competency_id: str = ""
    bloom: str = "remember"
    difficulty: str = "medium"
    marks: int = 1
    source: str = ""
    board: str = ""
    chapter: int = 0
    topic: str = ""
    official_answer: str = ""
    question: str = ""

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class EvidenceRecord:
    evidence_id: str
    learner_id: str
    concept_id: str = ""
    competency_id: str = ""
    source: str = "assessment"
    correct: bool | None = None
    score: float = 0.0  # 0–1
    confidence: float | None = None  # learner self-rating 0–1
    item_id: str = ""
    notes: str = ""
    timestamp: str = ""
    weight: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class MasteryRecord:
    learner_id: str
    concept_id: str
    level: str = "beginning"
    mastery_pct: float = 0.0
    evidence_count: int = 0
    evidence_ids: list[str] = field(default_factory=list)
    last_updated: str = ""
    recommended_next: str = ""
    learning_outcome_ids: list[str] = field(default_factory=list)
    competency_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class CompetencyProgress:
    learner_id: str
    competency_id: str
    name: str = ""
    current_level: str = "beginning"
    mastery_pct: float = 0.0
    evidence: list[str] = field(default_factory=list)
    last_updated: str = ""
    recommended_next: str = ""
    history: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class MisconceptionHit:
    misconception_id: str
    label: str
    concept_id: str = ""
    evidence: str = ""
    confidence: float = 0.0
    intervention_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class InterventionRec:
    intervention_id: str
    kind: str
    title: str
    description: str = ""
    concept_id: str = ""
    priority: int = 50
    accessibility_profiles: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class AttemptResult:
    attempt_id: str
    learner_id: str
    assessment_id: str
    item_id: str
    response: str
    correct: bool | None
    official_answer: str = ""
    score: float = 0.0
    concept_id: str = ""
    bloom: str = ""
    time_sec: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
