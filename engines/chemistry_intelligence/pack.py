"""Chemistry Intelligence Pack — SubjectIntelligencePack implementation."""

from __future__ import annotations

from typing import Any, Mapping

from engines.chemistry_intelligence.accessibility import chemistry_accessibility_for_uli
from engines.chemistry_intelligence.diagrams import recommend_visuals_for_text
from engines.chemistry_intelligence.domains import (
    concept_graph_from_uli,
    detect_domains,
    prerequisite_hints,
)
from engines.chemistry_intelligence.equations import inspect_equations_and_notation
from engines.chemistry_intelligence.laboratory import build_laboratory_scaffolds
from engines.chemistry_intelligence.misconceptions import detect_chemistry_misconceptions
from engines.chemistry_intelligence.molecular_models import molecular_from_uli
from engines.chemistry_intelligence.pedagogy import (
    assessment_hints,
    lxp_interaction_hints,
    revision_summary,
    teaching_strategies,
    tutor_guidance,
)
from engines.chemistry_intelligence.validators import collect_chemistry_quality_signals
from engines.chemistry_intelligence.worked_examples import build_worked_example_scaffolds
from engines.chemistry_intelligence._domain_views import (
    analyse_acids_bases,
    analyse_atomic_structure,
    analyse_chemical_bonding,
    analyse_electrochemistry,
    analyse_equilibrium,
    analyse_inorganic,
    analyse_kinetics,
    analyse_laboratory,
    analyse_organic,
    analyse_periodic_table,
    analyse_reactions,
    analyse_stoichiometry,
    analyse_thermochemistry,
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
    except Exception:  # noqa: BLE001
        pass
    try:
        stem = dict(uli.stem_structure())
        for c in stem.get("claims_found") or []:
            if isinstance(c, Mapping):
                parts.append(str(c.get("raw") or c.get("text") or ""))
        for eq in stem.get("chemical_equations") or []:
            if isinstance(eq, Mapping):
                parts.append(str(eq.get("raw") or ""))
            else:
                parts.append(str(eq))
    except Exception:  # noqa: BLE001
        pass
    return "\n".join(p for p in parts if p)


class ChemistryIntelligencePack(SubjectIntelligencePack):
    """
    Authoritative chemistry teaching layer for Alora AI (SIF Phase 3).

    Enriches ULI with pedagogy, molecular, equation, and laboratory metadata.
    Never invents chemistry, never balances beyond Computation Layer artifacts.
    """

    def __init__(self) -> None:
        self.subject = SubjectId("chemistry", "Chemistry", "stem")
        self.version = PACK_VERSION

    def capabilities(self) -> list[SubjectCapability]:
        return [
            SubjectCapability("chemistry.teaching", "Inquiry / POE / CER / CRA strategies", "teaching", True),
            SubjectCapability("chemistry.assessment", "Bloom/DOK/lab-skill hints for AME", "assessment", True),
            SubjectCapability("chemistry.visual", "Molecular / reaction / lab diagram recommendations", "visual", True),
            SubjectCapability("chemistry.accessibility", "Notation TTS, alt text, cognitive-load guidance", "accessibility", True),
            SubjectCapability("chemistry.tutor", "Socratic / mole scaffolding / reaction reasoning", "tutor", True),
            SubjectCapability("chemistry.lxp", "Periodic table / 3D molecule / balancing hooks", "lxp", True),
            SubjectCapability("chemistry.laboratory", "Lab + safety metadata scaffolds", "teaching", True),
            SubjectCapability("chemistry.molecular", "Formula / Lewis / functional-group metadata", "visual", True),
            SubjectCapability("chemistry.equations", "Equation metadata over verified STEM outputs", "teaching", True),
            SubjectCapability("chemistry.misconceptions", "Pattern-based chemistry misconception library", "teaching", True),
        ]

    def analyse_lesson(self, uli: Any, context: Mapping[str, Any] | None = None) -> SubjectAnalysisResult:
        ctx = dict(context or {})
        exam_mode = bool(ctx.get("exam_mode") or ctx.get("protected_assessment"))
        text = _uli_text(uli)
        domains = detect_domains(text)
        misconceptions = detect_chemistry_misconceptions(text)
        graph = concept_graph_from_uli(uli, domains)
        graph["prerequisites"] = prerequisite_hints(domains)
        visuals = recommend_visuals_for_text(text)
        scaffolds = build_worked_example_scaffolds(uli, exam_mode=exam_mode)
        labs = build_laboratory_scaffolds(uli)
        equations = inspect_equations_and_notation(uli)
        molecular = molecular_from_uli(uli)
        quality = collect_chemistry_quality_signals(uli)
        domain_facets = {
            "atomic_structure": analyse_atomic_structure(text),
            "periodic_table": analyse_periodic_table(text),
            "chemical_bonding": analyse_chemical_bonding(text),
            "reactions": analyse_reactions(text),
            "stoichiometry": analyse_stoichiometry(text),
            "acids_bases": analyse_acids_bases(text),
            "organic": analyse_organic(text),
            "inorganic": analyse_inorganic(text),
            "electrochemistry": analyse_electrochemistry(text),
            "thermochemistry": analyse_thermochemistry(text),
            "kinetics": analyse_kinetics(text),
            "equilibrium": analyse_equilibrium(text),
            "laboratory": analyse_laboratory(text),
        }
        teach = teaching_strategies(domains)
        assess = assessment_hints(uli, domains)
        revision = revision_summary(domains, misconceptions)
        a11y = chemistry_accessibility_for_uli(uli)
        tutor = tutor_guidance(misconceptions, scaffolds)
        lxp = lxp_interaction_hints(visuals, molecular, labs)
        interactions = [
            {"interaction_id": h.get("hook_id"), "meta": h}
            for h in lxp
            if h.get("hook_id") and not str(h.get("hook_id")).startswith("recommended_")
        ]

        warnings: list[str] = []
        if not domains:
            warnings.append("No chemistry domain markers detected in ULI text; enrichment is minimal.")
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
                "pack": "chemistry_intelligence",
                "version": self.version,
                "domains": domains,
                "domain_facets": domain_facets,
                "worked_examples": scaffolds,
                "laboratory": labs,
                "equations": equations,
                "molecular": molecular,
                "quality_signals": quality.get("teaching"),
                "exam_mode": exam_mode,
                "mutates_curriculum": False,
                "context_keys": list(ctx.keys()),
            },
        )
