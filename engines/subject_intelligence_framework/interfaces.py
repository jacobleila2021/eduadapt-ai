"""Subject Intelligence Framework — plug-in interface contract."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping

from engines.subject_intelligence_framework.schemas import (
    SubjectAnalysisResult,
    SubjectCapability,
    SubjectId,
)


class SubjectIntelligencePack(ABC):
    """
    Every subject plug-in implements this interface.

    Packs enrich ULI semantically. They must never invent verified curriculum
    facts, never call LLMs for factual content, and never mutate EngineResults.
    """

    subject: SubjectId
    version: str = "0.0.0-placeholder"

    @abstractmethod
    def capabilities(self) -> list[SubjectCapability]:
        """Declare teaching/visual/assessment/LXP capabilities (may be unavailable)."""

    @abstractmethod
    def analyse_lesson(self, uli: Any, context: Mapping[str, Any] | None = None) -> SubjectAnalysisResult:
        ...

    def build_concept_graph(self, uli: Any, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
        return self.analyse_lesson(uli, context).concept_graph

    def detect_misconceptions(self, uli: Any, context: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.analyse_lesson(uli, context).misconceptions

    def recommend_visuals(self, uli: Any, context: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.analyse_lesson(uli, context).visuals

    def recommend_interactions(self, uli: Any, context: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.analyse_lesson(uli, context).interactions

    def build_assessment_hints(self, uli: Any, context: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.analyse_lesson(uli, context).assessment_hints

    def build_revision_summary(self, uli: Any, context: Mapping[str, Any] | None = None) -> dict[str, Any]:
        return self.analyse_lesson(uli, context).revision_summary

    def build_accessibility_guidance(
        self, uli: Any, context: Mapping[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        return self.analyse_lesson(uli, context).accessibility_guidance

    def build_tutor_guidance(self, uli: Any, context: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.analyse_lesson(uli, context).tutor_guidance

    def build_lxp_hints(self, uli: Any, context: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
        return self.analyse_lesson(uli, context).lxp_hints


class PlaceholderSubjectPack(SubjectIntelligencePack):
    """Registered stub — returns empty structured payloads until a real pack lands."""

    def __init__(self, subject: SubjectId) -> None:
        self.subject = subject
        self.version = "0.0.0-placeholder"

    def capabilities(self) -> list[SubjectCapability]:
        return [
            SubjectCapability(
                capability_id=f"{self.subject.key}.teaching",
                label=f"{self.subject.display_name} teaching strategies",
                category="teaching",
                available=False,
                notes="Placeholder — implement in subject pack milestone.",
            ),
            SubjectCapability(
                capability_id=f"{self.subject.key}.assessment",
                label=f"{self.subject.display_name} assessment hints",
                category="assessment",
                available=False,
            ),
            SubjectCapability(
                capability_id=f"{self.subject.key}.visual",
                label=f"{self.subject.display_name} visualisation guidance",
                category="visual",
                available=False,
            ),
            SubjectCapability(
                capability_id=f"{self.subject.key}.accessibility",
                label=f"{self.subject.display_name} accessibility guidance",
                category="accessibility",
                available=False,
            ),
            SubjectCapability(
                capability_id=f"{self.subject.key}.tutor",
                label=f"{self.subject.display_name} AI tutor guidance",
                category="tutor",
                available=False,
            ),
            SubjectCapability(
                capability_id=f"{self.subject.key}.lxp",
                label=f"{self.subject.display_name} LXP interaction hints",
                category="lxp",
                available=False,
            ),
        ]

    def analyse_lesson(self, uli: Any, context: Mapping[str, Any] | None = None) -> SubjectAnalysisResult:
        return SubjectAnalysisResult(
            subject_key=self.subject.key,
            ok=True,
            placeholder=True,
            warnings=[
                f"Subject pack '{self.subject.key}' is a placeholder; no subject-specific enrichment applied."
            ],
            metadata={"context_keys": list((context or {}).keys())},
        )
