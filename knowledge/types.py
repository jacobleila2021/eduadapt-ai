"""Knowledge Layer shared types."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class KnowledgeChunk:
    chunk_id: str
    text: str
    chapter: int
    chapter_title: str
    page_start: int | None
    source: str
    board: str
    grade: str
    subject: str
    keywords: list[str] = field(default_factory=list)

    def citation(self) -> str:
        page = f" p.{self.page_start}" if self.page_start else ""
        return f"[NCERT Class {self.grade} {self.subject} Ch.{self.chapter}{page}]"


@dataclass
class RagHit:
    chunk_id: str
    text: str
    score: float
    citation: str
    chapter_title: str
    metadata: dict


@dataclass
class OfficialMcq:
    item_id: str
    source: str
    subject: str
    grade: str
    chapter: int
    topic: str
    question_type: str
    question: str
    options: list[str]
    official_answer: str
    explanation: str
    marks: int
    board: str
    bloom: str = "remember"
    year: str = ""
    difficulty: str = "medium"
    learning_objective: str = ""
    tags: list[str] = field(default_factory=list)
