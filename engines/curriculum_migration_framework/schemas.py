"""CMIF schemas — production migration jobs & package contracts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

PIPELINE_STAGES = (
    "import",
    "validate",
    "normalize",
    "map_ucf",
    "extract_metadata",
    "extract_learning_outcomes",
    "extract_assessments",
    "extract_diagrams",
    "extract_formulae",
    "extract_glossary",
    "accessibility_metadata",
    "knowledge_graph",
    "semantic_chunking",
    "vector_index",
    "version_package",
    "quality_assurance",
    "publish",
)

SUPPORTED_SOURCE_TYPES = (
    "pdf",
    "docx",
    "epub",
    "html",
    "markdown",
    "xml",
    "json",
    "zip",
    "lms",
    "government_repo",
    "publisher_package",
    "university_repo",
    "professional_repo",
    "api_connector",
    "inline_json",
)

PACKAGE_LIFECYCLE = ("draft", "review", "published", "deprecated", "archived")

SUPPORTED_BOARDS = (
    "ncert",
    "cbse",
    "icse",
    "isc",
    "cambridge",
    "ib",
    "kerala_scert",
    "state_board",
    "nios",
    "university",
    "professional",
)


@dataclass
class MigrationJob:
    job_id: str
    board: str
    source_type: str
    status: str = "queued"  # queued|running|paused|failed|completed|rejected
    stage: str = "import"
    package_id: str = ""
    curriculum_id: str = ""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    audit: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    resume_token: str = ""
    quality_score: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
