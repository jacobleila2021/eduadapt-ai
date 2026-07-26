"""Biology Intelligence Pack — SubjectIntelligencePack implementation."""

from __future__ import annotations

from typing import Any, Mapping

from engines.biology_intelligence.accessibility import biology_accessibility_for_uli
from engines.biology_intelligence.diagrams import recommend_visuals_for_text
from engines.biology_intelligence.domains import (
    concept_graph_from_uli,
    detect_domains,
    prerequisite_hints,
)
from engines.biology_intelligence.laboratory import build_laboratory_scaffolds
from engines.biology_intelligence.misconceptions import detect_biology_misconceptions
from engines.biology_intelligence.pedagogy import (
    assessment_hints,
    lxp_interaction_hints,
    revision_summary,
    teaching_strategies,
    tutor_guidance,
)
from engines.biology_intelligence.processes import build_process_metadata
from engines.biology_intelligence.terminology import inspect_terminology_and_taxonomy
from engines.biology_intelligence.validators import collect_biology_quality_signals
from engines.biology_intelligence.worked_examples import build_worked_example_scaffolds
from engines.biology_intelligence._domain_views import (
    analyse_anatomy,
    analyse_biotechnology,
    analyse_cell_biology,
    analyse_ecology,
    analyse_evolution,
    analyse_genetics,
    analyse_human_biology,
    analyse_laboratory,
    analyse_microbiology,
    analyse_physiology,
    analyse_plant_biology,
    analyse_taxonomy,
)
from engines.subject_intelligence_framework.interfaces import SubjectIntelligencePack
from engines.subject_intelligence_framework.schemas import (
    SubjectAnalysisResult,
    SubjectCapability,
    SubjectId,
)

PACK_VERSION = "1.0.0"


def _uli_text(uli: Any) -> str:
    parts: list[str] = []
    try:
        env = uli.source_envelope
        if isinstance(env, Mapping):
            parts.append(str(env.get("normalized_text") or env.get("text") or ""))
        else:
            parts.append(str(getattr(env, "normalized_text", "") or getattr(env, "text", "") or ""))
    except Exception:  # noqa: BLE001
        pass
    try:
        learn = dict(uli.learning_structure())
        for c in learn.get("key_concepts") or []:
            if isinstance(c, Mapping):
                parts.append(str(c.get("concept") or ""))
        for o in learn.get("learning_objectives") or []:
            if isinstance(o, Mapping):
                parts.append(str(o.get("objective") or ""))
            else:
                parts.append(str(o))
        for v in learn.get("vocabulary") or []:
            if isinstance(v, Mapping):
                parts.append(str(v.get("term") or ""))
    except Exception:  # noqa: BLE001
        pass
    try:
        stem = dict(uli.stem_structure())
        for c in stem.get("claims_found") or []:
            if isinstance(c, Mapping):
                parts.append(str(c.get("raw") or c.get("text") or ""))
        for term in stem.get("biological_terminology") or []:
            if isinstance(term, Mapping):
                parts.append(str(term.get("term") or term.get("raw") or ""))
            else:
                parts.append(str(term))
    except Exception:  # noqa: BLE001
        pass
    return "\n".join(p for p in parts if p)


class BiologyIntelligencePack(SubjectIntelligencePack):
    """
    Authoritative biology teaching layer for Alora AI (SIF Phase 4).

    Enriches ULI with life-systems, diagram, process, and laboratory metadata.
    Never invents biology facts or mutates EngineResults.
    """

    def __init__(self) -> None:
        self.subject = SubjectId("biology", "Biology", "stem")
        self.version = PACK_VERSION

    def capabilities(self) -> list[SubjectCapability]:
        return [
            SubjectCapability("biology.teaching", "Inquiry / systems / structure–function strategies", "teaching", True),
            SubjectCapability("biology.assessment", "Bloom/DOK/practical biology hints for AME", "assessment", True),
            SubjectCapability("biology.visual", "Cell / anatomy / ecology diagram recommendations", "visual", True),
            SubjectCapability("biology.accessibility", "Diagram descriptions, TTS terms, lab a11y", "accessibility", True),
            SubjectCapability("biology.tutor", "Socratic / inquiry / misconception diagnosis", "tutor", True),
            SubjectCapability("biology.lxp", "Anatomy viewers / life-cycle / food-web hooks", "lxp", True),
            SubjectCapability("biology.laboratory", "Microscopy / investigation / safety scaffolds", "teaching", True),
            SubjectCapability("biology.processes", "Pathways, life cycles, systems metadata", "teaching", True),
            SubjectCapability("biology.misconceptions", "Pattern-based biology misconception library", "teaching", True),
        ]

    def analyse_lesson(self, uli: Any, context: Mapping[str, Any] | None = None) -> SubjectAnalysisResult:
        ctx = dict(context or {})
        exam_mode = bool(ctx.get("exam_mode") or ctx.get("protected_assessment"))
        text = _uli_text(uli)
        domains = detect_domains(text)
        misconceptions = detect_biology_misconceptions(text)
        graph = concept_graph_from_uli(uli, domains)
        graph["prerequisites"] = prerequisite_hints(domains)
        visuals = recommend_visuals_for_text(text)
        scaffolds = build_worked_example_scaffolds(uli, exam_mode=exam_mode)
        labs = build_laboratory_scaffolds(uli)
        processes = build_process_metadata(text, domains)
        terminology = inspect_terminology_and_taxonomy(uli)
        quality = collect_biology_quality_signals(uli)
        domain_facets = {
            "cell_biology": analyse_cell_biology(text),
            "human_biology": analyse_human_biology(text),
            "plant_biology": analyse_plant_biology(text),
            "genetics": analyse_genetics(text),
            "evolution": analyse_evolution(text),
            "ecology": analyse_ecology(text),
            "microbiology": analyse_microbiology(text),
            "anatomy": analyse_anatomy(text),
            "physiology": analyse_physiology(text),
            "taxonomy": analyse_taxonomy(text),
            "laboratory": analyse_laboratory(text),
            "biotechnology": analyse_biotechnology(text),
        }
        teach = teaching_strategies(domains)
        assess = assessment_hints(uli, domains)
        revision = revision_summary(domains, misconceptions)
        a11y = biology_accessibility_for_uli(uli)
        tutor = tutor_guidance(misconceptions, scaffolds)
        lxp = lxp_interaction_hints(visuals, processes, labs)
        interactions = [
            {"interaction_id": h.get("hook_id"), "meta": h}
            for h in lxp
            if h.get("hook_id") and not str(h.get("hook_id")).startswith("recommended_")
        ]

        warnings: list[str] = []
        if not domains:
            warnings.append("No biology domain markers detected in ULI text; enrichment is minimal.")
        if exam_mode:
            warnings.append("Exam/protected mode: worked-example final verification omitted.")

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
            metadata={
                "pack": "biology_intelligence",
                "version": self.version,
                "domains": domains,
                "domain_facets": domain_facets,
                "worked_examples": scaffolds,
                "laboratory": labs,
                "processes": processes,
                "terminology": terminology,
                "quality_signals": quality.get("teaching"),
                "exam_mode": exam_mode,
                "mutates_curriculum": False,
                "context_keys": list(ctx.keys()),
            },
        )
