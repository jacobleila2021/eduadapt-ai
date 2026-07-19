"""Universal Curriculum Framework — canonical academic schema (not a curriculum)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SUPPORTED_BOARDS = (
    "CBSE",
    "NCERT",
    "ICSE",
    "ISC",
    "Cambridge",
    "IB",
    "NIOS",
    "State Board",
    "Kerala SCERT",
    "University",
    "Professional",
    "Corporate",
)

TAXONOMIES = (
    "blooms",
    "dok",
    "solo",
    "marzano",
    "21st_century",
    "future_skills",
    "critical_thinking",
    "computational_thinking",
    "scientific_inquiry",
)


@dataclass
class BoardMetadata:
    board_id: str
    board_name: str
    country: str = "IN"
    region: str = ""
    curriculum_version: str = "1.0.0"
    publication_year: int | None = None
    copyright_status: str = "restricted"
    language: str = "en"
    medium_of_instruction: str = "English"
    academic_calendar: str = ""
    assessment_system: str = ""
    credits: str = ""
    certification: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AcademicStructure:
    program: str = ""
    stage: str = ""  # primary|secondary|higher_secondary|tertiary|professional
    grade: str = ""
    year: str = ""
    semester: str = ""
    term: str = ""
    subject: str = ""
    stream: str = ""
    unit: str = ""
    chapter: str = ""
    chapter_number: int = 0
    topic: str = ""
    subtopic: str = ""
    learning_sequence: int = 0
    estimated_teaching_hours: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LearningObjectivesBlock:
    knowledge: list[str] = field(default_factory=list)
    skill: list[str] = field(default_factory=list)
    competency: list[str] = field(default_factory=list)
    performance_indicators: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    essential_questions: list[str] = field(default_factory=list)
    big_ideas: list[str] = field(default_factory=list)
    misconceptions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompetencyNode:
    competency_id: str
    description: str
    mastery_indicators: list[str] = field(default_factory=list)
    progression_level: str = "developing"  # emerging|developing|proficient|advanced
    transfer_skills: list[str] = field(default_factory=list)
    future_readiness_skills: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TaxonomyTags:
    blooms: str = "understand"
    dok: str = "2"
    solo: str = ""
    marzano: str = ""
    skills_21st: list[str] = field(default_factory=list)
    future_skills: list[str] = field(default_factory=list)
    critical_thinking: bool = False
    computational_thinking: bool = False
    scientific_inquiry: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PrerequisiteGraph:
    previous_concepts: list[str] = field(default_factory=list)
    current_concepts: list[str] = field(default_factory=list)
    future_concepts: list[str] = field(default_factory=list)
    cross_disciplinary_links: list[dict[str, str]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AssessmentMeta:
    objectives: list[str] = field(default_factory=list)
    question_types: list[str] = field(default_factory=list)
    marks: float | None = None
    difficulty: str = "medium"
    competency_ids: list[str] = field(default_factory=list)
    bloom: str = ""
    dok: str = ""
    official_answers: list[str] = field(default_factory=list)
    rubrics: list[str] = field(default_factory=list)
    scoring_guides: list[str] = field(default_factory=list)
    common_misconceptions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AccessibilityMeta:
    reading_level: str = ""
    vocabulary_complexity: str = "medium"
    cognitive_load: str = "medium"
    recommended_presentation_modes: list[str] = field(default_factory=list)
    suggested_accommodations: list[str] = field(default_factory=list)
    alternative_modalities: list[str] = field(default_factory=list)
    language_support: list[str] = field(default_factory=list)
    accessibility_tags: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class UCFTopic:
    """Atomic teachable unit in the Universal Curriculum Framework."""

    topic_id: str
    title: str
    board: BoardMetadata
    structure: AcademicStructure
    objectives: LearningObjectivesBlock = field(default_factory=LearningObjectivesBlock)
    competencies: list[CompetencyNode] = field(default_factory=list)
    taxonomy: TaxonomyTags = field(default_factory=TaxonomyTags)
    prerequisites: PrerequisiteGraph = field(default_factory=PrerequisiteGraph)
    assessment: AssessmentMeta = field(default_factory=AssessmentMeta)
    accessibility: AccessibilityMeta = field(default_factory=AccessibilityMeta)
    formula_ids: list[str] = field(default_factory=list)
    diagram_ids: list[str] = field(default_factory=list)
    glossary_ids: list[str] = field(default_factory=list)
    question_bank_ids: list[str] = field(default_factory=list)
    version: str = "1.0.0"
    deprecated: bool = False
    source_labels: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "topic_id": self.topic_id,
            "title": self.title,
            "board": self.board.to_dict(),
            "structure": self.structure.to_dict(),
            "objectives": self.objectives.to_dict(),
            "competencies": [c.to_dict() for c in self.competencies],
            "taxonomy": self.taxonomy.to_dict(),
            "prerequisites": self.prerequisites.to_dict(),
            "assessment": self.assessment.to_dict(),
            "accessibility": self.accessibility.to_dict(),
            "formula_ids": self.formula_ids,
            "diagram_ids": self.diagram_ids,
            "glossary_ids": self.glossary_ids,
            "question_bank_ids": self.question_bank_ids,
            "version": self.version,
            "deprecated": self.deprecated,
            "source_labels": self.source_labels,
        }


@dataclass
class UCFPackage:
    """Versioned curriculum package in UCF form."""

    package_id: str
    board: BoardMetadata
    structure: AcademicStructure
    topics: list[UCFTopic] = field(default_factory=list)
    formulae: list[dict[str, Any]] = field(default_factory=list)
    diagrams: list[dict[str, Any]] = field(default_factory=list)
    glossary: list[dict[str, Any]] = field(default_factory=list)
    questions: list[dict[str, Any]] = field(default_factory=list)
    version: str = "1.0.0"
    supersedes: str = ""
    status: str = "active"  # active|deprecated|draft

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_id": self.package_id,
            "schema": "ucf/1.0",
            "board": self.board.to_dict(),
            "structure": self.structure.to_dict(),
            "topics": [t.to_dict() for t in self.topics],
            "formulae": self.formulae,
            "diagrams": self.diagrams,
            "glossary": self.glossary,
            "questions": self.questions,
            "version": self.version,
            "supersedes": self.supersedes,
            "status": self.status,
        }
