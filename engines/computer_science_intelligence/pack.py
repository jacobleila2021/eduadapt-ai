"""Computer Science Intelligence Pack — SubjectIntelligencePack implementation."""

from __future__ import annotations

from typing import Any, Mapping

from engines.computer_science_intelligence.accessibility import computer_science_accessibility_for_uli
from engines.computer_science_intelligence.algorithms import algorithms_metadata
from engines.computer_science_intelligence.analytics import analytics_metadata
from engines.computer_science_intelligence.artificial_intelligence import artificial_intelligence_metadata
from engines.computer_science_intelligence.assessment import computer_science_assessment_hints
from engines.computer_science_intelligence.cloud_computing import cloud_computing_metadata
from engines.computer_science_intelligence.competencies import competency_metadata
from engines.computer_science_intelligence.computational_thinking import computational_thinking_metadata
from engines.computer_science_intelligence.cybersecurity import cybersecurity_metadata
from engines.computer_science_intelligence.data_structures import data_structures_metadata
from engines.computer_science_intelligence.databases import databases_metadata
from engines.computer_science_intelligence.digital_literacy import digital_literacy_metadata
from engines.computer_science_intelligence.domains import (
    concept_graph_from_uli,
    detect_domains,
    prerequisite_hints,
)
from engines.computer_science_intelligence.machine_learning import machine_learning_metadata
from engines.computer_science_intelligence.metadata import build_pack_metadata
from engines.computer_science_intelligence.misconceptions import detect_computer_science_misconceptions
from engines.computer_science_intelligence.networking import networking_metadata
from engines.computer_science_intelligence.operating_systems import operating_systems_metadata
from engines.computer_science_intelligence.pedagogy import (
    companion_metadata,
    lxp_hints,
    recommend_visuals,
    revision_summary,
    teaching_strategies,
    tutor_guidance,
)
from engines.computer_science_intelligence.programming import programming_metadata
from engines.computer_science_intelligence.robotics import robotics_metadata
from engines.computer_science_intelligence.validation import collect_computer_science_quality_signals
from engines.computer_science_intelligence.web_development import web_development_metadata
from engines.subject_intelligence_core.utilities import extract_uli_text
from engines.subject_intelligence_framework.interfaces import SubjectIntelligencePack
from engines.subject_intelligence_framework.schemas import (
    SubjectAnalysisResult,
    SubjectCapability,
    SubjectId,
)

PACK_VERSION = "1.0.0"


class ComputerScienceIntelligencePack(SubjectIntelligencePack):
    """
    Authoritative computer science teaching layer for Alora AI.

    Covers computational thinking, programming, algorithms, databases, networking,
    cybersecurity, AI literacy, and related domains without inventing curriculum.
    """

    def __init__(self) -> None:
        self.subject = SubjectId("computer_science", "Computer Science", "stem")
        self.version = PACK_VERSION

    def capabilities(self) -> list[SubjectCapability]:
        return [
            SubjectCapability("cs.computational_thinking", "CT / decomposition / abstraction", "teaching", True),
            SubjectCapability("cs.programming", "Programming & debugging scaffolds", "teaching", True),
            SubjectCapability("cs.algorithms", "Algorithms & complexity metadata", "teaching", True),
            SubjectCapability("cs.databases", "Database / SQL / ER metadata", "teaching", True),
            SubjectCapability("cs.networking", "Networking & cybersecurity metadata", "teaching", True),
            SubjectCapability("cs.ai_literacy", "Conceptual AI / ML / ethics metadata", "teaching", True),
            SubjectCapability("cs.assessment", "Coding/debug/trace assessment hints", "assessment", True),
            SubjectCapability("cs.accessibility", "Dyslexia-friendly code / a11y", "accessibility", True),
            SubjectCapability("cs.tutor", "Socratic debugging for ATIE", "tutor", True),
            SubjectCapability("cs.lxp", "Code viewer / animations / diagrams", "lxp", True),
        ]

    def analyse_lesson(self, uli: Any, context: Mapping[str, Any] | None = None) -> SubjectAnalysisResult:
        ctx = dict(context or {})
        exam_mode = bool(ctx.get("exam_mode") or ctx.get("protected_assessment"))
        text = extract_uli_text(uli, include_vocabulary=True)
        domains = detect_domains(text)
        misconceptions = detect_computer_science_misconceptions(text)
        graph = concept_graph_from_uli(uli, domains)
        prereq = prerequisite_hints(domains)
        graph["prerequisites"] = prereq

        ct = computational_thinking_metadata(text, domains)
        programming = programming_metadata(text, domains, exam_mode=exam_mode)
        algorithms = algorithms_metadata(text, domains)
        data_structures = data_structures_metadata(text, domains)
        databases = databases_metadata(text, domains)
        networking = networking_metadata(text, domains)
        operating_systems = operating_systems_metadata(text, domains)
        cybersecurity = cybersecurity_metadata(text, domains)
        web = web_development_metadata(text, domains)
        ai = artificial_intelligence_metadata(text, domains)
        ml = machine_learning_metadata(text, domains)
        robotics = robotics_metadata(text, domains)
        cloud = cloud_computing_metadata(text, domains)
        digital = digital_literacy_metadata(text, domains)

        visuals = recommend_visuals(text, domains)
        teach = teaching_strategies(domains)
        assess = computer_science_assessment_hints(uli, domains)
        revision = revision_summary(domains, misconceptions)
        a11y = computer_science_accessibility_for_uli(uli)
        tutor = tutor_guidance(misconceptions)
        companion = companion_metadata(domains)
        analytics = analytics_metadata(domains, misconceptions)
        competencies = competency_metadata(domains, prereq)
        quality = collect_computer_science_quality_signals(uli)
        lxp = lxp_hints(visuals)
        interactions = [
            {"interaction_id": h.get("hook_id"), "meta": h}
            for h in lxp
            if h.get("hook_id") and not str(h.get("hook_id")).startswith("recommended_")
        ]

        warnings: list[str] = []
        if not domains:
            warnings.append("No computer science domain markers detected; enrichment is minimal.")
        if exam_mode:
            warnings.append("Exam/protected mode: do not reveal coding assessment answers.")

        return SubjectAnalysisResult(
            subject_key=self.subject.key,
            ok=True,
            placeholder=False,
            concept_graph=graph,
            misconceptions=misconceptions,
            visuals=visuals,
            interactions=interactions,
            assessment_hints=assess,
            revision_summary=revision,
            accessibility_guidance=a11y,
            teaching_strategies=teach,
            tutor_guidance=tutor,
            lxp_hints=lxp,
            warnings=warnings,
            metadata=build_pack_metadata(
                version=self.version,
                domains=domains,
                exam_mode=exam_mode,
                extra={
                    "computational_thinking": ct,
                    "programming": programming,
                    "algorithms": algorithms,
                    "data_structures": data_structures,
                    "databases": databases,
                    "networking": networking,
                    "operating_systems": operating_systems,
                    "cybersecurity": cybersecurity,
                    "web_development": web,
                    "artificial_intelligence": ai,
                    "machine_learning": ml,
                    "robotics": robotics,
                    "cloud_computing": cloud,
                    "digital_literacy": digital,
                    "companion": companion,
                    "analytics": analytics,
                    "competencies": competencies,
                    "quality_signals": quality.get("teaching"),
                    "context_keys": list(ctx.keys()),
                },
            ),
        )
