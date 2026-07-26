"""Physics Intelligence Pack — SubjectIntelligencePack implementation."""

from __future__ import annotations

from typing import Any, Mapping

from engines.physics_intelligence.accessibility import physics_accessibility_for_uli
from engines.physics_intelligence.assessment import physics_assessment_hints_for_uli
from engines.physics_intelligence.domains import (
    concept_graph_from_uli,
    detect_domains,
    prerequisite_hints,
)
from engines.physics_intelligence.experiments import build_experiment_scaffolds
from engines.physics_intelligence.misconceptions import detect_physics_misconceptions
from engines.physics_intelligence.pedagogy import (
    lxp_interaction_hints,
    revision_summary,
    teaching_strategies,
    tutor_guidance,
)
from engines.physics_intelligence.units_formulas import inspect_formula_and_units
from engines.physics_intelligence.validators import collect_physics_quality_signals
from engines.physics_intelligence.visualizations import recommend_visuals_for_text
from engines.physics_intelligence.worked_examples import build_worked_example_scaffolds
from engines.physics_intelligence._domain_views import (
    analyse_electricity,
    analyse_energy,
    analyse_forces,
    analyse_magnetism,
    analyse_measurements,
    analyse_mechanics,
    analyse_momentum,
    analyse_motion,
    analyse_optics,
    analyse_thermodynamics,
    analyse_waves,
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
        for expr in stem.get("scientific_calculations") or []:
            if isinstance(expr, Mapping):
                parts.append(str(expr.get("raw") or ""))
            else:
                parts.append(str(expr))
    except Exception:  # noqa: BLE001
        pass
    return "\n".join(p for p in parts if p)


class PhysicsIntelligencePack(SubjectIntelligencePack):
    """
    Authoritative physics teaching layer for Alora AI (SIF Phase 2).

    Enriches ULI with pedagogy, experiment, and modelling metadata.
    Never invents physics facts or mutates EngineResults.
    """

    def __init__(self) -> None:
        self.subject = SubjectId("physics", "Physics", "stem")
        self.version = PACK_VERSION

    def capabilities(self) -> list[SubjectCapability]:
        return [
            SubjectCapability(
                "physics.teaching",
                "Inquiry / POE / CER / CRA / conceptual change strategies",
                "teaching",
                True,
            ),
            SubjectCapability(
                "physics.assessment",
                "Bloom/DOK/scientific-practice hints for AME",
                "assessment",
                True,
            ),
            SubjectCapability(
                "physics.visual",
                "Force/ray/circuit/wave diagram recommendations",
                "visual",
                True,
            ),
            SubjectCapability(
                "physics.accessibility",
                "Simplified language, diagram descriptions, TTS units",
                "accessibility",
                True,
            ),
            SubjectCapability(
                "physics.tutor",
                "Socratic / experimental reasoning / error diagnosis for ATIE",
                "tutor",
                True,
            ),
            SubjectCapability(
                "physics.lxp",
                "Simulation / circuit / ray / force-vector interaction hooks",
                "lxp",
                True,
            ),
            SubjectCapability(
                "physics.experiments",
                "Experiment metadata scaffolds (aim, variables, CER, safety)",
                "teaching",
                True,
            ),
            SubjectCapability(
                "physics.misconceptions",
                "Pattern-based physics misconception library",
                "teaching",
                True,
            ),
            SubjectCapability(
                "physics.units_formulas",
                "Unit / formula consistency inspection over STEM outputs",
                "teaching",
                True,
            ),
        ]

    def analyse_lesson(self, uli: Any, context: Mapping[str, Any] | None = None) -> SubjectAnalysisResult:
        ctx = dict(context or {})
        exam_mode = bool(ctx.get("exam_mode") or ctx.get("protected_assessment"))
        text = _uli_text(uli)
        domains = detect_domains(text)
        misconceptions = detect_physics_misconceptions(text)
        graph = concept_graph_from_uli(uli, domains)
        graph["prerequisites"] = prerequisite_hints(domains)
        visuals = recommend_visuals_for_text(text)
        scaffolds = build_worked_example_scaffolds(uli, exam_mode=exam_mode)
        experiments = build_experiment_scaffolds(uli)
        units = inspect_formula_and_units(uli)
        quality = collect_physics_quality_signals(uli)
        domain_facets = {
            "mechanics": analyse_mechanics(text),
            "motion": analyse_motion(text),
            "forces": analyse_forces(text),
            "energy": analyse_energy(text),
            "momentum": analyse_momentum(text),
            "electricity": analyse_electricity(text),
            "magnetism": analyse_magnetism(text),
            "optics": analyse_optics(text),
            "waves": analyse_waves(text),
            "thermodynamics": analyse_thermodynamics(text),
            "measurements": analyse_measurements(text),
        }
        teach = teaching_strategies(domains)
        assess = physics_assessment_hints_for_uli(uli, domains)
        revision = revision_summary(domains, misconceptions)
        a11y = physics_accessibility_for_uli(uli)
        tutor = tutor_guidance(misconceptions, scaffolds)
        lxp = lxp_interaction_hints(visuals, experiments)
        interactions = [
            {"interaction_id": h.get("hook_id"), "meta": h}
            for h in lxp
            if h.get("hook_id") and not str(h.get("hook_id")).startswith("recommended_")
        ]

        warnings: list[str] = []
        if not domains:
            warnings.append("No physics domain markers detected in ULI text; enrichment is minimal.")
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
                "pack": "physics_intelligence",
                "version": self.version,
                "domains": domains,
                "domain_facets": domain_facets,
                "worked_examples": scaffolds,
                "experiments": experiments,
                "units_formulas": units,
                "quality_signals": quality.get("teaching"),
                "exam_mode": exam_mode,
                "mutates_curriculum": False,
                "context_keys": list(ctx.keys()),
            },
        )
