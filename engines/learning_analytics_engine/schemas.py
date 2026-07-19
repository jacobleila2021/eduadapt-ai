"""Learning Analytics & Insights Engine schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

ROLES = (
    "student",
    "teacher",
    "parent",
    "special_educator",
    "school",
    "district",
    "administrator",
    "enterprise",
    "government",
)

ALERT_TYPES = (
    "learning_regression",
    "low_engagement",
    "missed_assignments",
    "accessibility_concern",
    "mastery_decline",
    "rapid_improvement",
    "assessment_readiness",
    "teacher_attention",
    "parent_follow_up",
)


@dataclass
class InsightRecommendation:
    recommendation_id: str
    audience: str
    title: str
    reason: str
    evidence: list[dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.75
    priority: int = 50
    expected_outcome: str = ""
    kind: str = "intervention"  # intervention|enrichment|accessibility|practice|revision

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class AnalyticsAlert:
    alert_id: str
    alert_type: str
    severity: str  # low|medium|high
    message: str
    learner_id: str = ""
    evidence: list[dict[str, Any]] = field(default_factory=list)
    threshold: float | None = None
    actionable: bool = True

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass
class MetricPoint:
    name: str
    value: float | int | str | None
    unit: str = ""
    explanation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()
