"""Schemas for Universal Lesson Intelligence Validation & Quality Engine (ULIQE)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping


class FindingSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class CertificationLevel(str, Enum):
    PRODUCTION_READY = "Production Ready"
    GOLD = "Gold"
    SILVER = "Silver"
    NEEDS_REVIEW = "Needs Review"
    REJECTED = "Rejected"


CATEGORY_WEIGHTS: dict[str, float] = {
    "curriculum_accuracy": 0.25,
    "completeness": 0.20,
    "pedagogy": 0.15,
    "stem_accuracy": 0.10,
    "accessibility": 0.10,
    "assessment_coverage": 0.10,
    "semantic_integrity": 0.10,
}


@dataclass(frozen=True)
class ValidationFinding:
    rule_id: str
    category: str
    severity: FindingSeverity
    message: str
    field_path: str = ""
    recommendation: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        def _jsonable(value: Any) -> Any:
            if isinstance(value, Mapping):
                return {str(k): _jsonable(v) for k, v in value.items()}
            if isinstance(value, (list, tuple)):
                return [_jsonable(v) for v in value]
            if isinstance(value, FindingSeverity):
                return value.value
            return value

        return {
            "rule_id": self.rule_id,
            "category": self.category,
            "severity": self.severity.value,
            "message": self.message,
            "field_path": self.field_path,
            "recommendation": self.recommendation,
            "evidence": _jsonable(self.evidence),
        }


@dataclass
class CategoryScore:
    category: str
    weight: float
    score: float  # 0–100
    applicable: bool = True
    findings_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ULIQEReport:
    """Auditable validation report for one ULI object."""

    ok: bool
    certification: CertificationLevel
    overall_score: float
    confidence: float
    pass_fail: str
    findings: list[ValidationFinding] = field(default_factory=list)
    category_scores: list[CategoryScore] = field(default_factory=list)
    missing_elements: list[str] = field(default_factory=list)
    inconsistencies: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    curriculum_gaps: list[str] = field(default_factory=list)
    accessibility_gaps: list[str] = field(default_factory=list)
    assessment_gaps: list[str] = field(default_factory=list)
    semantic_issues: list[str] = field(default_factory=list)
    stem_issues: list[str] = field(default_factory=list)
    rules_executed: list[str] = field(default_factory=list)
    uli_source_id: str = ""
    uli_schema_version: str = ""
    grounding_mode: str = "uploaded_source"
    engine_version: str = "1.0.0"
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def downstream_allowed(self) -> bool:
        """Only Production Ready may auto-flow to downstream engines."""
        return self.certification == CertificationLevel.PRODUCTION_READY

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "certification": self.certification.value,
            "overall_score": self.overall_score,
            "confidence": self.confidence,
            "pass_fail": self.pass_fail,
            "downstream_allowed": self.downstream_allowed,
            "findings": [f.to_dict() for f in self.findings],
            "category_scores": [c.to_dict() for c in self.category_scores],
            "missing_elements": list(self.missing_elements),
            "inconsistencies": list(self.inconsistencies),
            "recommendations": list(self.recommendations),
            "warnings": list(self.warnings),
            "curriculum_gaps": list(self.curriculum_gaps),
            "accessibility_gaps": list(self.accessibility_gaps),
            "assessment_gaps": list(self.assessment_gaps),
            "semantic_issues": list(self.semantic_issues),
            "stem_issues": list(self.stem_issues),
            "rules_executed": list(self.rules_executed),
            "uli_source_id": self.uli_source_id,
            "uli_schema_version": self.uli_schema_version,
            "grounding_mode": self.grounding_mode,
            "engine_version": self.engine_version,
            "metadata": dict(self.metadata),
        }
