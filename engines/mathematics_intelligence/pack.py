"""Mathematics Intelligence Pack — SubjectIntelligencePack implementation."""

from __future__ import annotations

from typing import Any, Mapping

from engines.mathematics_intelligence.accessibility import math_accessibility_for_uli
from engines.mathematics_intelligence.assessment import math_assessment_hints_for_uli
from engines.mathematics_intelligence.domains import (
    concept_graph_from_uli,
    detect_domains,
    prerequisite_hints,
)
from engines.mathematics_intelligence.misconceptions import detect_math_misconceptions
from engines.mathematics_intelligence.pedagogy import (
    lxp_interaction_hints,
    teaching_strategies,
    tutor_guidance,
)
from engines.mathematics_intelligence.revision import math_revision_for_domains
from engines.mathematics_intelligence.symbolic import inspect_symbolic_consistency
from engines.mathematics_intelligence.validators import collect_math_quality_signals
from engines.mathematics_intelligence.visualizations import recommend_visuals_for_text
from engines.mathematics_intelligence.worked_examples import build_worked_example_scaffolds
from engines.mathematics_intelligence._domain_views import (
    analyse_algebra,
    analyse_arithmetic,
    analyse_calculus,
    analyse_geometry,
    analyse_number_systems,
    analyse_probability,
    analyse_statistics,
    analyse_trigonometry,
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
        for expr in stem.get("mathematical_expressions") or []:
            if isinstance(expr, Mapping):
                parts.append(str(expr.get("raw") or ""))
            else:
                parts.append(str(expr))
    except Exception:  # noqa: BLE001
        pass
    return "\n".join(p for p in parts if p)


class MathematicsIntelligencePack(SubjectIntelligencePack):
    """
    Authoritative mathematics teaching layer for Alora AI (SIF Phase 1).

    Enriches ULI with pedagogy metadata. Never invents curriculum facts,
    never mutates EngineResults, never solves beyond Computation Layer outputs.
    """

    def __init__(self) -> None:
        self.subject = SubjectId("mathematics", "Mathematics", "stem")
        self.version = PACK_VERSION

    def capabilities(self) -> list[SubjectCapability]:
        return [
            SubjectCapability(
                "mathematics.teaching",
                "CRA / explicit instruction / GRR / productive struggle / retrieval",
                "teaching",
                True,
                notes="Pedagogical strategy metadata only",
            ),
            SubjectCapability(
                "mathematics.assessment",
                "Bloom/DOK/difficulty diagnostic hints for AME",
                "assessment",
                True,
            ),
            SubjectCapability(
                "mathematics.visual",
                "Verified visual type recommendations (LXP/VMLE render)",
                "visual",
                True,
            ),
            SubjectCapability(
                "mathematics.accessibility",
                "Dyslexia-friendly notation & cognitive-load guidance for AIE",
                "accessibility",
                True,
            ),
            SubjectCapability(
                "mathematics.tutor",
                "Socratic / hints / fading / error diagnosis for ATIE",
                "tutor",
                True,
            ),
            SubjectCapability(
                "mathematics.lxp",
                "Interactive graph / walkthrough / formula-card hooks",
                "lxp",
                True,
            ),
            SubjectCapability(
                "mathematics.revision",
                "Spaced / interleaved revision metadata",
                "revision",
                True,
            ),
            SubjectCapability(
                "mathematics.misconceptions",
                "Pattern-based misconception library",
                "teaching",
                True,
            ),
            SubjectCapability(
                "mathematics.symbolic",
                "Symbolic consistency inspection over STEM artifacts",
                "teaching",
                True,
            ),
        ]

    def analyse_lesson(self, uli: Any, context: Mapping[str, Any] | None = None) -> SubjectAnalysisResult:
        ctx = dict(context or {})
        exam_mode = bool(ctx.get("exam_mode") or ctx.get("protected_assessment"))
        text = _uli_text(uli)
        domains = detect_domains(text)
        misconceptions = detect_math_misconceptions(text)
        graph = concept_graph_from_uli(uli, domains)
        graph["prerequisites"] = prerequisite_hints(domains)
        visuals = recommend_visuals_for_text(text)
        scaffolds = build_worked_example_scaffolds(uli, exam_mode=exam_mode)
        symbolic = inspect_symbolic_consistency(uli)
        quality = collect_math_quality_signals(uli)
        domain_facets = {
            "arithmetic": analyse_arithmetic(text),
            "algebra": analyse_algebra(text),
            "geometry": analyse_geometry(text),
            "trigonometry": analyse_trigonometry(text),
            "calculus": analyse_calculus(text),
            "statistics": analyse_statistics(text),
            "probability": analyse_probability(text),
            "number_systems": analyse_number_systems(text),
        }
        teach = teaching_strategies(domains)
        assess = math_assessment_hints_for_uli(uli, domains)
        revision = math_revision_for_domains(domains, misconceptions)
        a11y = math_accessibility_for_uli(uli)
        tutor = tutor_guidance(misconceptions, scaffolds)
        lxp = lxp_interaction_hints(visuals)
        interactions = [
            {"interaction_id": h.get("hook_id"), "meta": h}
            for h in lxp
            if h.get("hook_id") and not str(h.get("hook_id")).startswith("recommended_")
        ]

        warnings: list[str] = []
        if not domains:
            warnings.append("No mathematics domain markers detected in ULI text; enrichment is minimal.")
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
                "pack": "mathematics_intelligence",
                "version": self.version,
                "domains": domains,
                "domain_facets": domain_facets,
                "worked_examples": scaffolds,
                "symbolic": symbolic,
                "quality_signals": quality.get("teaching"),
                "exam_mode": exam_mode,
                "mutates_curriculum": False,
                "context_keys": list(ctx.keys()),
            },
        )
