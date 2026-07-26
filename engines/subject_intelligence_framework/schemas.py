"""Subject Intelligence Framework (SIF) — schemas."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class SubjectId:
    """Stable plug-in identifier (curriculum-agnostic)."""

    key: str
    display_name: str
    family: str = "general"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SubjectCapability:
    """Declares what a pack can offer — LXP/ATIE consume descriptions, not implementations."""

    capability_id: str
    label: str
    category: str  # teaching | assessment | visual | accessibility | tutor | lxp | revision
    available: bool = False
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SubjectAnalysisResult:
    """Normalized output of SubjectPack.analyse_lesson (and related hooks)."""

    subject_key: str
    ok: bool = True
    placeholder: bool = True
    concept_graph: dict[str, Any] = field(default_factory=dict)
    misconceptions: list[dict[str, Any]] = field(default_factory=list)
    visuals: list[dict[str, Any]] = field(default_factory=list)
    interactions: list[dict[str, Any]] = field(default_factory=list)
    assessment_hints: list[dict[str, Any]] = field(default_factory=list)
    revision_summary: dict[str, Any] = field(default_factory=dict)
    accessibility_guidance: list[dict[str, Any]] = field(default_factory=list)
    teaching_strategies: list[dict[str, Any]] = field(default_factory=list)
    tutor_guidance: list[dict[str, Any]] = field(default_factory=list)
    lxp_hints: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SubjectDetection:
    subject_key: str
    confidence: float
    provenance: str
    candidates: list[str] = field(default_factory=list)
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
