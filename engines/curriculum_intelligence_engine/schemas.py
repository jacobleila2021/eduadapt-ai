"""Unified curriculum model — curriculum-agnostic internal representation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# Curriculum → Programme → Grade → Subject → Unit → Chapter → Topic →
# Concept → Learning Objective → Competency → Assessment Outcome → Resources


@dataclass
class CurriculumRef:
    curriculum_id: str
    board: str
    programme: str = ""
    grade: str = ""
    subject: str = ""
    version: str = "1.0.0"
    language: str = "en"
    original_labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "curriculum_id": self.curriculum_id,
            "board": self.board,
            "programme": self.programme,
            "grade": self.grade,
            "subject": self.subject,
            "version": self.version,
            "language": self.language,
            "original_labels": self.original_labels,
        }


@dataclass
class ConceptNode:
    concept_id: str
    title: str
    definition: str = ""
    subject: str = ""
    grade_range: list[str] = field(default_factory=list)
    difficulty: str = "medium"
    chapter: int = 0
    chapter_title: str = ""
    topic: str = ""
    bloom: str = "understand"
    dok: str = ""  # Webb's Depth of Knowledge 1–4
    prerequisites: list[str] = field(default_factory=list)
    learning_objective_ids: list[str] = field(default_factory=list)
    competency_ids: list[str] = field(default_factory=list)
    related_concepts: list[str] = field(default_factory=list)
    visual_resources: list[str] = field(default_factory=list)
    assessment_links: list[str] = field(default_factory=list)
    adaptation_keys: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    board: str = "Unknown"
    original_term: str = ""

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class LearningOutcome:
    outcome_id: str
    statement: str
    bloom: str = "understand"
    dok: str = "2"
    concept_ids: list[str] = field(default_factory=list)
    competency_ids: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    board: str = "Unknown"
    grade: str = ""
    subject: str = ""
    chapter: int = 0
    equivalent_ids: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class Competency:
    competency_id: str
    name: str
    description: str = ""
    skills: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    mastery_threshold: float = 0.8
    assessment_methods: list[str] = field(default_factory=list)
    related_concepts: list[str] = field(default_factory=list)
    accessibility_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class PrerequisiteEdge:
    from_concept: str
    to_concept: str
    relation: str = "requires"  # requires | strengthens | spiral
    strength: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class CrossCurriculumLink:
    concept_id: str
    board: str
    programme: str = ""
    label: str = ""
    grade: str = ""
    notes: str = ""
    link_type: str = "equivalent"  # equivalent | advanced | optional | missing

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class ProgressionLevel:
    level: str  # beginning | developing | proficient | advanced | mastered
    description: str = ""
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


PROGRESSION_ORDER = ("beginning", "developing", "proficient", "advanced", "mastered")

ADAPTATION_PROFILES = (
    "dyslexia",
    "dysgraphia",
    "dyscalculia",
    "adhd",
    "autism",
    "executive_function",
    "ell",
    "visual",
    "auditory",
    "gifted",
    "twice_exceptional",
)
