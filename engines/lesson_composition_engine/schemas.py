"""Lesson Composition Engine (LCE) schemas — educational composition contracts.

LCE composes verified knowledge into premium lessons. It never invents curriculum,
equations, answers, or scientific diagrams. Those remain Knowledge / Computation Layer.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

LCE_SCHEMA_VERSION = "1.0.0"
PACK_VERSION = LCE_SCHEMA_VERSION
LCE_ENGINE_ID = "lesson_composition"
PRODUCTION_THRESHOLD = 0.78

METADATA_LEAK_PATTERNS = (
    r"\blearning objectives?\b",
    r"\bgrade level\b",
    r"\btime allocation\b",
    r"\bsubject\s*:\s*",
    r"\bcurriculum standards?\b",
    r"\bas an ai\b",
    r"\bdelve into\b",
    r"\blet'?s dive\b",
    r"\bneed_engine:",
    r"\bneed_source:",
)

# Adaptive versions LCE intentionally authors (pedagogically distinct).
ADAPTIVE_VERSION_IDS = (
    "standard",
    "vocabulary",
    "ld",  # neurodiversity / mainstream support scaffold
    "ell",
    "visual",
    "auditory",
    "teacher",
    "parent",
    "worksheet",
    "adhd",
    "autism",
    "dyslexia",
)

QUALITY_CATEGORIES = (
    "flow_quality",
    "teaching_quality",
    "vocabulary_quality",
    "visual_placement",
    "diagram_quality",
    "reading_quality",
    "accessibility",
    "consistency",
    "subject_quality",
    "publication_quality",
)

SUBJECT_TEACHING_SEQUENCES: dict[str, tuple[str, ...]] = {
    "mathematics": (
        "concrete",
        "visual",
        "representation",
        "symbols",
        "worked_example",
        "practice",
        "application",
    ),
    "physics": (
        "concept",
        "phenomenon",
        "experiment",
        "diagram",
        "formula",
        "example",
        "practice",
    ),
    "chemistry": (
        "concept",
        "particle_view",
        "reaction",
        "equation",
        "diagram",
        "safety",
        "application",
    ),
    "biology": (
        "concept",
        "process",
        "diagram",
        "labels",
        "analogy",
        "application",
    ),
    "english": (
        "reading",
        "vocabulary",
        "grammar",
        "writing",
        "speaking",
        "listening",
        "literature",
    ),
    "social_science": (
        "context",
        "timeline",
        "map",
        "cause_effect",
        "primary_source",
        "citizenship",
        "inquiry",
    ),
    "computer_science": (
        "concept",
        "algorithm",
        "flowchart",
        "code",
        "memory",
        "execution_trace",
        "practice",
    ),
    "commerce": (
        "scenario",
        "accounting",
        "graph",
        "case_study",
        "decision",
        "application",
    ),
    "world_languages": (
        "pronunciation",
        "sentence_building",
        "culture",
        "listening",
        "speaking",
        "practice",
    ),
    "general": (
        "hook",
        "explain",
        "example",
        "visual",
        "practice",
        "summary",
        "reflection",
    ),
}

CONCEPT_TEACHING_STEPS = (
    "concept",
    "simple_explanation",
    "real_life_example",
    "visual",
    "worked_example",
    "common_misconception",
    "practice_question",
    "reflection",
)

VOCAB_CARD_FIELDS = (
    "term",
    "pronunciation",
    "part_of_speech",
    "definition",
    "simple_explanation",
    "example_sentence",
    "picture",
    "synonyms",
    "antonyms",
    "related_concepts",
    "difficulty",
    "reading_level",
    "color",
)


@dataclass
class VocabularyCard:
    term: str
    pronunciation: str = ""
    part_of_speech: str = "noun"
    definition: str = ""  # student-friendly by default
    simple_explanation: str = ""
    academic_definition: str = ""
    example_sentence: str = ""
    memory_tip: str = ""
    lesson_context: str = ""
    picture: str = ""
    synonyms: list[str] = field(default_factory=list)
    antonyms: list[str] = field(default_factory=list)
    related_concepts: list[str] = field(default_factory=list)
    difficulty: str = "core"
    reading_level: str = "grade_appropriate"
    color: str = "#e6f7f8"
    emoji: str = ""
    verified: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_word_wall_row(self) -> dict[str, Any]:
        """Backward-compatible word_wall row for existing renderers/exporters."""
        return {
            "term": self.term,
            "definition": self.simple_explanation or self.definition,
            "academic_definition": self.academic_definition or self.definition,
            "emoji": self.emoji or "📘",
            "visual_description": self.picture or self.simple_explanation,
            "child_friendly": self.simple_explanation or self.definition,
            "simple_explanation": self.simple_explanation or self.definition,
            "example": self.example_sentence,
            "example_sentence": self.example_sentence,
            "memory_tip": self.memory_tip,
            "lesson_context": self.lesson_context,
            "pronunciation": self.pronunciation,
            "part_of_speech": self.part_of_speech,
            "synonyms": list(self.synonyms),
            "antonyms": list(self.antonyms),
            "related_words": list(self.synonyms),
            "opposite_words": list(self.antonyms),
            "related_concepts": list(self.related_concepts),
            "difficulty": self.difficulty,
            "reading_level": self.reading_level,
            "color": self.color,
            "picture": self.picture,
            "verified": self.verified,
            "lce_card": True,
            "pqle_card": True,
        }


@dataclass
class ConceptBlock:
    concept_id: str
    title: str
    simple_explanation: str = ""
    real_life_example: str = ""
    visual_id: str = ""
    worked_example: str = ""
    misconception: str = ""
    practice_question: str = ""
    reflection: str = ""
    body_paragraphs: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LessonSection:
    section_id: str
    title: str
    role: str  # hook|teach|example|practice|summary|revision|reflection|application|...
    body: str = ""
    paragraphs: list[str] = field(default_factory=list)
    box: str = ""
    visual_ids: list[str] = field(default_factory=list)
    concept_id: str = ""
    transition_in: str = ""
    transition_out: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_lesson_section(self) -> dict[str, Any]:
        body = self.body
        if not body and self.paragraphs:
            body = "\n\n".join(self.paragraphs)
        return {
            "title": self.title,
            "body": body,
            "box": self.box,
            "role": self.role,
            "visual_ids": list(self.visual_ids),
            "concept_id": self.concept_id,
            "transition_in": self.transition_in,
            "lce": True,
        }


@dataclass
class VisualPlacement:
    visual_id: str
    after_section_id: str
    rationale: str = ""
    preferred_format: str = "svg"  # svg preferred; mermaid only if requested

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class QualityScore:
    category: str
    score: float
    notes: list[str] = field(default_factory=list)
    passed: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CompositionQualityReport:
    overall: float = 0.0
    scores: list[QualityScore] = field(default_factory=list)
    production_ready: bool = False
    reject_rendering: bool = False
    threshold: float = PRODUCTION_THRESHOLD
    version: str = LCE_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall": self.overall,
            "scores": [s.to_dict() for s in self.scores],
            "production_ready": self.production_ready,
            "reject_rendering": self.reject_rendering,
            "threshold": self.threshold,
            "version": self.version,
        }


@dataclass
class ComposedLesson:
    """Premium lesson authored by LCE for one adaptive version."""

    version_id: str
    title: str
    topic: str
    subject: str = "general"
    big_idea: str = ""
    sections: list[LessonSection] = field(default_factory=list)
    concept_blocks: list[ConceptBlock] = field(default_factory=list)
    vocabulary_cards: list[VocabularyCard] = field(default_factory=list)
    visual_placements: list[VisualPlacement] = field(default_factory=list)
    flowchart_svg: str = ""
    concept_map_svg: str = ""
    mermaid_diagram: str = ""  # empty unless explicitly requested
    svg_diagram: str = ""
    visual_summary: str = ""
    summary: str = ""
    revision_points: list[str] = field(default_factory=list)
    reflection_prompts: list[str] = field(default_factory=list)
    application_tasks: list[str] = field(default_factory=list)
    practice: list[dict[str, Any]] = field(default_factory=list)
    answer_key: list[dict[str, Any]] = field(default_factory=list)
    pedagogy_notes: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)
    lce_version: str = LCE_SCHEMA_VERSION

    def to_dict(self) -> dict[str, Any]:
        return {
            "version_id": self.version_id,
            "title": self.title,
            "topic": self.topic,
            "subject": self.subject,
            "big_idea": self.big_idea,
            "sections": [s.to_dict() for s in self.sections],
            "concept_blocks": [c.to_dict() for c in self.concept_blocks],
            "vocabulary_cards": [v.to_dict() for v in self.vocabulary_cards],
            "visual_placements": [v.to_dict() for v in self.visual_placements],
            "flowchart_svg": self.flowchart_svg,
            "concept_map_svg": self.concept_map_svg,
            "mermaid_diagram": self.mermaid_diagram,
            "svg_diagram": self.svg_diagram,
            "visual_summary": self.visual_summary,
            "summary": self.summary,
            "revision_points": list(self.revision_points),
            "reflection_prompts": list(self.reflection_prompts),
            "application_tasks": list(self.application_tasks),
            "practice": list(self.practice),
            "answer_key": list(self.answer_key),
            "pedagogy_notes": list(self.pedagogy_notes),
            "source_refs": list(self.source_refs),
            "lce_version": self.lce_version,
        }

    def to_adaptation_dict(self) -> dict[str, Any]:
        """Shape expected by structured_renderers / exporters."""
        sections = [s.to_lesson_section() for s in self.sections]
        out: dict[str, Any] = {
            "big_idea": self.big_idea,
            "sections": sections,
            "visual_summary": self.visual_summary,
            "mermaid_diagram": self.mermaid_diagram or "",
            "svg_diagram": self.svg_diagram or self.flowchart_svg or self.concept_map_svg,
            "flowchart_svg": self.flowchart_svg,
            "concept_map_svg": self.concept_map_svg,
            "summary": self.summary,
            "revision_points": list(self.revision_points),
            "reflection_prompts": list(self.reflection_prompts),
            "application_tasks": list(self.application_tasks),
            "practice": list(self.practice),
            "answer_key": list(self.answer_key),
            "topic": self.topic,
            "title": self.title,
            "lce": {
                "version_id": self.version_id,
                "subject": self.subject,
                "schema": self.lce_version,
                "concept_blocks": [c.to_dict() for c in self.concept_blocks],
                "visual_placements": [v.to_dict() for v in self.visual_placements],
                "pedagogy_notes": list(self.pedagogy_notes),
            },
        }
        return out


@dataclass
class CompositionBlueprint:
    """Plan produced before prose assembly — consumed by composer + optional LLM."""

    topic: str
    subject: str
    grade: str = ""
    objectives: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    vocabulary_terms: list[str] = field(default_factory=list)
    misconceptions: list[str] = field(default_factory=list)
    teaching_sequence: list[str] = field(default_factory=list)
    visual_intents: list[dict[str, Any]] = field(default_factory=list)
    stem_artifacts: list[dict[str, Any]] = field(default_factory=list)
    subject_pack_hints: dict[str, Any] = field(default_factory=dict)
    accessibility_hints: dict[str, Any] = field(default_factory=dict)
    source_excerpt: str = ""
    narrative_contract: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class LessonCompositionPackage:
    """Full LCE output for a lesson generation run."""

    blueprint: CompositionBlueprint
    standard: ComposedLesson | None = None
    versions: dict[str, dict[str, Any]] = field(default_factory=dict)
    vocabulary: dict[str, Any] = field(default_factory=dict)
    quality: CompositionQualityReport | None = None
    composed_by: str = LCE_ENGINE_ID
    schema_version: str = LCE_SCHEMA_VERSION
    # Publisher spine metadata for attach/UI (board, CLG, PQLE) — not learner HTML
    publisher_meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "blueprint": self.blueprint.to_dict(),
            "standard": self.standard.to_dict() if self.standard else {},
            "versions": self.versions,
            "vocabulary": self.vocabulary,
            "quality": self.quality.to_dict() if self.quality else {},
            "composed_by": self.composed_by,
            "schema_version": self.schema_version,
            "publisher_meta": dict(self.publisher_meta or {}),
        }


@dataclass
class ClgNode:
    node_id: str
    kind: str
    title: str
    text: str = ""
    source_refs: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "kind": self.kind,
            "title": self.title,
            "text": self.text,
            "source_refs": list(self.source_refs),
            "extra": dict(self.extra),
        }


@dataclass
class ClgEdge:
    edge_id: str
    source: str
    target: str
    relation: str
    label: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CanonicalLessonGraph:
    """Single educational truth before any prose is written."""

    topic: str
    subject_key: str = "general"
    learning_goals: list[dict[str, Any]] = field(default_factory=list)
    core_concepts: list[dict[str, Any]] = field(default_factory=list)
    facts: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    vocabulary: list[dict[str, Any]] = field(default_factory=list)
    misconceptions: list[dict[str, Any]] = field(default_factory=list)
    examples: list[dict[str, Any]] = field(default_factory=list)
    visual_refs: list[dict[str, Any]] = field(default_factory=list)
    assessment_outcomes: list[dict[str, Any]] = field(default_factory=list)
    accessibility_notes: list[dict[str, Any]] = field(default_factory=list)
    claim_texts: list[str] = field(default_factory=list)
    nodes: list[dict[str, Any]] = field(default_factory=list)
    edges: list[dict[str, Any]] = field(default_factory=list)
    provenance: dict[str, Any] = field(default_factory=dict)
    version: str = PACK_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EerlCheck:
    check_id: str
    label: str
    passed: bool
    score: float
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EerlReport:
    ok: bool
    overall_score: float
    production_ready: bool
    checks: list[dict[str, Any]] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    version: str = PACK_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
