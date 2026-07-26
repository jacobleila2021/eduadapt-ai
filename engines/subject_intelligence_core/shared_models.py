"""Shared educational models for Subject Intelligence Core Services."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class MisconceptionHit:
    misconception_id: str
    label: str
    domain: str
    matched_patterns: list[str]
    correction_strategy: str
    related_concepts: list[str]
    provenance: str
    confidence: float
    severity: str = "medium"
    remediation: dict[str, Any] = field(default_factory=dict)
    intervention: dict[str, Any] = field(default_factory=dict)
    evidence_links: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        # Packs historically omit empty remediation/intervention/evidence — keep lean default.
        base = {
            "misconception_id": self.misconception_id,
            "label": self.label,
            "domain": self.domain,
            "matched_patterns": self.matched_patterns,
            "correction_strategy": self.correction_strategy,
            "related_concepts": self.related_concepts,
            "provenance": self.provenance,
            "confidence": self.confidence,
        }
        if self.severity and self.severity != "medium":
            base["severity"] = self.severity
        if self.remediation:
            base["remediation"] = self.remediation
        if self.intervention:
            base["intervention"] = self.intervention
        if self.evidence_links:
            base["evidence_links"] = self.evidence_links
        return base


@dataclass
class FindingSeed:
    rule_id: str
    severity: str
    message: str
    category: str = "pedagogy"
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        out = {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "message": self.message,
            "category": self.category,
        }
        if self.evidence:
            out["evidence"] = self.evidence
        return out


@dataclass
class DiagramRecommendation:
    visual_type: str
    label: str
    domain: str
    renderer: str = "lxp_or_vmle"
    provenance: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class StrategyRef:
    id: str
    name: str
    family: str = "general"
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
