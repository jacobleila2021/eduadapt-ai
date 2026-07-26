"""Social Science Intelligence Pack — SubjectIntelligencePack implementation."""

from __future__ import annotations

from typing import Any, Mapping

from engines.social_science_intelligence.accessibility import social_science_accessibility_for_uli
from engines.social_science_intelligence.analytics import analytics_metadata
from engines.social_science_intelligence.assessment import social_science_assessment_hints
from engines.social_science_intelligence.cause_effect import cause_effect_metadata
from engines.social_science_intelligence.citizenship import citizenship_metadata
from engines.social_science_intelligence.civics import civics_metadata
from engines.social_science_intelligence.competencies import competency_metadata
from engines.social_science_intelligence.domains import (
    concept_graph_from_uli,
    detect_domains,
    prerequisite_hints,
)
from engines.social_science_intelligence.economics import economics_metadata
from engines.social_science_intelligence.environmental_studies import environmental_studies_metadata
from engines.social_science_intelligence.geography import geography_metadata
from engines.social_science_intelligence.history import history_metadata
from engines.social_science_intelligence.maps import map_metadata
from engines.social_science_intelligence.metadata import build_pack_metadata
from engines.social_science_intelligence.misconceptions import detect_social_science_misconceptions
from engines.social_science_intelligence.pedagogy import (
    companion_metadata,
    lxp_hints,
    recommend_visuals,
    revision_summary,
    teaching_strategies,
    tutor_guidance,
)
from engines.social_science_intelligence.political_science import political_science_metadata
from engines.social_science_intelligence.sociology import sociology_metadata
from engines.social_science_intelligence.source_analysis import source_analysis_metadata
from engines.social_science_intelligence.timelines import timeline_metadata
from engines.social_science_intelligence.validation import collect_social_science_quality_signals
from engines.subject_intelligence_core.utilities import extract_uli_text
from engines.subject_intelligence_framework.interfaces import SubjectIntelligencePack
from engines.subject_intelligence_framework.schemas import (
    SubjectAnalysisResult,
    SubjectCapability,
    SubjectId,
)

PACK_VERSION = "1.0.0"

_FAMILY_SUBJECTS: tuple[SubjectId, ...] = (
    SubjectId("social_science", "Social Science", "humanities"),
    SubjectId("history", "History", "humanities"),
    SubjectId("geography", "Geography", "humanities"),
    SubjectId("civics", "Civics", "humanities"),
    # `economics` subject key is owned by CEIP (advanced/business); SSIP still
    # enriches school-level economics markers when the lesson is social_science.
    SubjectId("environmental_science", "Environmental Science", "stem"),
)


class SocialScienceIntelligencePack(SubjectIntelligencePack):
    """
    Authoritative social science teaching layer for Alora AI.

    Covers history, geography, civics/political science, school economics,
    sociology, and environmental studies metadata without inventing curriculum.
    """

    def __init__(self, subject: SubjectId | None = None) -> None:
        self.subject = subject or _FAMILY_SUBJECTS[0]
        self.version = PACK_VERSION

    def capabilities(self) -> list[SubjectCapability]:
        prefix = self.subject.key
        return [
            SubjectCapability(f"{prefix}.history", "History / chronology / sources", "teaching", True),
            SubjectCapability(f"{prefix}.geography", "Geography / maps / climate", "teaching", True),
            SubjectCapability(f"{prefix}.civics", "Civics / citizenship / governance", "teaching", True),
            SubjectCapability(f"{prefix}.economics", "School-level economics metadata", "teaching", True),
            SubjectCapability(f"{prefix}.timelines_maps", "Interactive timeline & map hooks", "lxp", True),
            SubjectCapability(f"{prefix}.assessment", "Source/map/timeline assessment hints", "assessment", True),
            SubjectCapability(f"{prefix}.accessibility", "Map/timeline a11y guidance", "accessibility", True),
            SubjectCapability(f"{prefix}.tutor", "Source evaluation / civic debate prompts", "tutor", True),
        ]

    def analyse_lesson(self, uli: Any, context: Mapping[str, Any] | None = None) -> SubjectAnalysisResult:
        ctx = dict(context or {})
        exam_mode = bool(ctx.get("exam_mode") or ctx.get("protected_assessment"))
        text = extract_uli_text(uli, include_vocabulary=True)
        domains = detect_domains(text)
        misconceptions = detect_social_science_misconceptions(text)
        graph = concept_graph_from_uli(uli, domains)
        prereq = prerequisite_hints(domains)
        graph["prerequisites"] = prereq

        history = history_metadata(text, domains)
        geography = geography_metadata(text, domains)
        civics = civics_metadata(text, domains)
        political = political_science_metadata(text, domains)
        economics = economics_metadata(text, domains)
        sociology = sociology_metadata(text, domains)
        environmental = environmental_studies_metadata(text, domains)
        timelines = timeline_metadata(text, domains)
        maps = map_metadata(text, domains)
        sources = source_analysis_metadata(text, domains)
        cause_effect = cause_effect_metadata(text, domains)
        citizenship = citizenship_metadata(text, domains)

        visuals = recommend_visuals(text, domains)
        teach = teaching_strategies(domains)
        assess = social_science_assessment_hints(uli, domains)
        revision = revision_summary(domains, misconceptions)
        a11y = social_science_accessibility_for_uli(uli)
        tutor = tutor_guidance(misconceptions)
        companion = companion_metadata(domains)
        analytics = analytics_metadata(domains, misconceptions, timelines, maps)
        competencies = competency_metadata(domains, prereq)
        quality = collect_social_science_quality_signals(uli)
        lxp = lxp_hints(visuals, timelines, maps)
        interactions = [
            {"interaction_id": h.get("hook_id"), "meta": h}
            for h in lxp
            if h.get("hook_id") and not str(h.get("hook_id")).startswith("recommended_")
        ]

        warnings: list[str] = []
        if not domains:
            warnings.append("No social science domain markers detected; enrichment is minimal.")
        if exam_mode:
            warnings.append("Exam/protected mode: do not reveal source-based assessment answers.")

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
                    "history": history,
                    "geography": geography,
                    "civics": civics,
                    "political_science": political,
                    "economics": economics,
                    "sociology": sociology,
                    "environmental_studies": environmental,
                    "timelines": timelines,
                    "maps": maps,
                    "source_analysis": sources,
                    "cause_effect": cause_effect,
                    "citizenship": citizenship,
                    "companion": companion,
                    "analytics": analytics,
                    "competencies": competencies,
                    "quality_signals": quality.get("teaching"),
                    "family_pack": "social_science_intelligence",
                    "context_keys": list(ctx.keys()),
                },
            ),
        )


def iter_family_packs() -> list[SocialScienceIntelligencePack]:
    return [SocialScienceIntelligencePack(subject=s) for s in _FAMILY_SUBJECTS]
