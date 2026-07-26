"""Commerce & Economics Intelligence Pack — SubjectIntelligencePack implementation."""

from __future__ import annotations

from typing import Any, Mapping

from engines.commerce_economics_intelligence.accessibility import commerce_economics_accessibility_for_uli
from engines.commerce_economics_intelligence.accounting import accounting_metadata
from engines.commerce_economics_intelligence.analytics import analytics_metadata
from engines.commerce_economics_intelligence.assessment import commerce_economics_assessment_hints
from engines.commerce_economics_intelligence.business_studies import business_studies_metadata
from engines.commerce_economics_intelligence.commerce import commerce_metadata
from engines.commerce_economics_intelligence.competencies import competency_metadata
from engines.commerce_economics_intelligence.domains import (
    concept_graph_from_uli,
    detect_domains,
    prerequisite_hints,
)
from engines.commerce_economics_intelligence.economics import economics_metadata
from engines.commerce_economics_intelligence.entrepreneurship import entrepreneurship_metadata
from engines.commerce_economics_intelligence.finance import finance_metadata
from engines.commerce_economics_intelligence.financial_literacy import financial_literacy_metadata
from engines.commerce_economics_intelligence.management import management_metadata
from engines.commerce_economics_intelligence.marketing import marketing_metadata
from engines.commerce_economics_intelligence.metadata import build_pack_metadata
from engines.commerce_economics_intelligence.misconceptions import detect_commerce_economics_misconceptions
from engines.commerce_economics_intelligence.pedagogy import (
    companion_metadata,
    lxp_hints,
    recommend_visuals,
    revision_summary,
    teaching_strategies,
    tutor_guidance,
)
from engines.commerce_economics_intelligence.taxation import taxation_metadata
from engines.commerce_economics_intelligence.validation import collect_commerce_economics_quality_signals
from engines.subject_intelligence_core.utilities import extract_uli_text
from engines.subject_intelligence_framework.interfaces import SubjectIntelligencePack
from engines.subject_intelligence_framework.schemas import (
    SubjectAnalysisResult,
    SubjectCapability,
    SubjectId,
)

PACK_VERSION = "1.0.0"

_FAMILY_SUBJECTS: tuple[SubjectId, ...] = (
    SubjectId("commerce", "Commerce", "commerce"),
    SubjectId("economics", "Economics", "commerce"),
    SubjectId("business_studies", "Business Studies", "commerce"),
)


class CommerceEconomicsIntelligencePack(SubjectIntelligencePack):
    """
    Authoritative commerce & economics teaching layer for Alora AI.

    Covers accounting, economics, business studies, finance, entrepreneurship,
    marketing, management, taxation, and financial literacy without inventing curriculum.
    """

    def __init__(self, subject: SubjectId | None = None) -> None:
        self.subject = subject or _FAMILY_SUBJECTS[0]
        self.version = PACK_VERSION

    def capabilities(self) -> list[SubjectCapability]:
        prefix = self.subject.key
        return [
            SubjectCapability(f"{prefix}.accounting", "Accounting / statements / ratios", "teaching", True),
            SubjectCapability(f"{prefix}.economics", "Micro/macro economics metadata", "teaching", True),
            SubjectCapability(f"{prefix}.business", "Business studies / management", "teaching", True),
            SubjectCapability(f"{prefix}.finance", "Finance / markets / literacy", "teaching", True),
            SubjectCapability(f"{prefix}.entrepreneurship", "Start-ups / canvas / validation", "teaching", True),
            SubjectCapability(f"{prefix}.assessment", "Case/numerical/scenario hints", "assessment", True),
            SubjectCapability(f"{prefix}.accessibility", "Tables / workflows / a11y", "accessibility", True),
            SubjectCapability(f"{prefix}.tutor", "Accounting & business reasoning for ATIE", "tutor", True),
            SubjectCapability(f"{prefix}.lxp", "Balance sheets / graphs / canvas", "lxp", True),
        ]

    def analyse_lesson(self, uli: Any, context: Mapping[str, Any] | None = None) -> SubjectAnalysisResult:
        ctx = dict(context or {})
        exam_mode = bool(ctx.get("exam_mode") or ctx.get("protected_assessment"))
        text = extract_uli_text(uli, include_vocabulary=True)
        domains = detect_domains(text)
        misconceptions = detect_commerce_economics_misconceptions(text)
        graph = concept_graph_from_uli(uli, domains)
        prereq = prerequisite_hints(domains)
        graph["prerequisites"] = prereq

        accounting = accounting_metadata(text, domains, exam_mode=exam_mode)
        economics = economics_metadata(text, domains)
        business = business_studies_metadata(text, domains)
        finance = finance_metadata(text, domains)
        entrepreneurship = entrepreneurship_metadata(text, domains)
        management = management_metadata(text, domains)
        marketing = marketing_metadata(text, domains)
        taxation = taxation_metadata(text, domains)
        commerce = commerce_metadata(text, domains)
        financial_literacy = financial_literacy_metadata(text, domains)

        visuals = recommend_visuals(text, domains)
        teach = teaching_strategies(domains)
        assess = commerce_economics_assessment_hints(uli, domains)
        revision = revision_summary(domains, misconceptions)
        a11y = commerce_economics_accessibility_for_uli(uli)
        tutor = tutor_guidance(misconceptions)
        companion = companion_metadata(domains)
        analytics = analytics_metadata(domains, misconceptions)
        competencies = competency_metadata(domains, prereq)
        quality = collect_commerce_economics_quality_signals(uli)
        lxp = lxp_hints(visuals)
        interactions = [
            {"interaction_id": h.get("hook_id"), "meta": h}
            for h in lxp
            if h.get("hook_id") and not str(h.get("hook_id")).startswith("recommended_")
        ]

        warnings: list[str] = []
        if not domains:
            warnings.append("No commerce/economics domain markers detected; enrichment is minimal.")
        if exam_mode:
            warnings.append("Exam/protected mode: do not reveal accounting or case assessment answers.")

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
                    "accounting": accounting,
                    "economics": economics,
                    "business_studies": business,
                    "finance": finance,
                    "entrepreneurship": entrepreneurship,
                    "management": management,
                    "marketing": marketing,
                    "taxation": taxation,
                    "commerce": commerce,
                    "financial_literacy": financial_literacy,
                    "companion": companion,
                    "analytics": analytics,
                    "competencies": competencies,
                    "quality_signals": quality.get("teaching"),
                    "family_pack": "commerce_economics_intelligence",
                    "context_keys": list(ctx.keys()),
                },
            ),
        )


def iter_family_packs() -> list[CommerceEconomicsIntelligencePack]:
    return [CommerceEconomicsIntelligencePack(subject=s) for s in _FAMILY_SUBJECTS]
