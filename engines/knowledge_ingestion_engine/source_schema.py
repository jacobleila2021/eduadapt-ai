"""Versioned, curriculum-neutral source ingestion contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

BlockKind = Literal[
    "prose",
    "heading",
    "table",
    "image_text",
    "speaker_notes",
    "unknown",
]


@dataclass(frozen=True)
class ContentBlock:
    block_id: str
    text: str
    kind: BlockKind = "prose"
    page: int | None = None
    slide: int | None = None
    order: int = 0
    extraction_method: str = "native"
    ocr_confidence: float | None = None
    source_ref: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SourceDocumentEnvelope:
    schema_version: str
    source_id: str
    source_hash: str
    filename: str
    detected_mime: str
    detected_format: str
    status: Literal["readable", "partial", "unreadable", "rejected"]
    blocks: list[ContentBlock] = field(default_factory=list)
    text: str = ""
    extraction_methods: list[str] = field(default_factory=list)
    ocr_used: bool = False
    ocr_confidence: float | None = None
    readable_content_score: float = 0.0
    language: str = "unknown"
    warnings: list[dict[str, Any]] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    user_metadata: dict[str, Any] = field(default_factory=dict)
    curriculum_resolution: dict[str, Any] = field(
        default_factory=lambda: {
            "status": "unknown",
            "curriculum": None,
            "confidence": 0.0,
            "provenance": "not_evaluated",
        }
    )

    @property
    def ok(self) -> bool:
        return self.status in {"readable", "partial"} and bool(self.text.strip())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["ok"] = self.ok
        return data
