"""Knowledge Ingestion Engine schemas — curriculum-agnostic internal model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".epub",
    ".txt",
    ".html",
    ".htm",
    ".md",
    ".markdown",
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".zip",
}


@dataclass
class CurriculumTag:
    curriculum: str = "Unknown"
    board: str = "Unknown"
    grade: str = ""
    subject: str = ""
    chapter: int = 0
    chapter_title: str = ""
    topic: str = ""
    unit: str = ""
    language: str = "en"

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class ExtractedEquation:
    latex: str
    kind: str = "math"  # math | chemistry | physics | statistics
    page: int | None = None
    raw: str = ""

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class ExtractedQuestion:
    question: str
    question_type: str = "short_answer"
    marks: int = 1
    bloom: str = "remember"
    difficulty: str = "medium"
    topic: str = ""
    chapter: int = 0
    official_answer: str = ""
    options: list[str] = field(default_factory=list)
    source: str = ""

    def to_dict(self) -> dict[str, Any]:
        d = self.__dict__.copy()
        return d


@dataclass
class KnowledgePackage:
    """Verified Knowledge Package — one per ingested lesson/document."""

    package_id: str
    schema_version: str = "1.0.0"
    source_path: str = ""
    source_hash: str = ""
    curriculum: dict[str, Any] = field(default_factory=dict)
    text_chunks: list[dict[str, Any]] = field(default_factory=list)
    figures: list[dict[str, Any]] = field(default_factory=list)
    tables: list[dict[str, Any]] = field(default_factory=list)
    equations: list[dict[str, Any]] = field(default_factory=list)
    questions: list[dict[str, Any]] = field(default_factory=list)
    vocabulary: list[str] = field(default_factory=list)
    learning_objectives: list[str] = field(default_factory=list)
    concepts: list[str] = field(default_factory=list)
    accessibility: dict[str, Any] = field(default_factory=dict)
    citations: list[str] = field(default_factory=list)
    index_status: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_id": self.package_id,
            "schema_version": self.schema_version,
            "source_path": self.source_path,
            "source_hash": self.source_hash,
            "curriculum": self.curriculum,
            "text_chunks": self.text_chunks,
            "figures": self.figures,
            "tables": self.tables,
            "equations": self.equations,
            "questions": self.questions,
            "vocabulary": self.vocabulary,
            "learning_objectives": self.learning_objectives,
            "concepts": self.concepts,
            "accessibility": self.accessibility,
            "citations": self.citations,
            "index_status": self.index_status,
            "version": self.version,
            "errors": self.errors,
            "warnings": self.warnings,
        }
