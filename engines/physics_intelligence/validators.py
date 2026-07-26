"""Physics quality signals for ULIQE — additive findings only; never change certify rules."""

from __future__ import annotations

from typing import Any, Mapping

from engines.physics_intelligence.domains import detect_domains
from engines.physics_intelligence.experiments import (
    build_experiment_scaffolds,
    experiment_completeness_signals,
)
from engines.physics_intelligence.misconceptions import detect_physics_misconceptions
from engines.physics_intelligence.units_formulas import inspect_formula_and_units
from engines.physics_intelligence.visualizations import recommend_visuals_for_text


def _source_text(uli: Any) -> str:
    parts: list[str] = []
    try:
        env = dict(uli.source_envelope or {})
        parts.append(str(env.get("normalized_text") or env.get("text") or ""))
    except Exception:  # noqa: BLE001
        pass
    try:
        learn = dict(uli.learning_structure())
        for c in learn.get("key_concepts") or []:
            if isinstance(c, Mapping):
                parts.append(str(c.get("concept") or ""))
    except Exception:  # noqa: BLE001
        pass
    return "\n".join(p for p in parts if p)


def collect_physics_quality_signals(uli: Any) -> dict[str, Any]:
    text = _source_text(uli)
    domains = detect_domains(text)
    misconceptions = detect_physics_misconceptions(text)
    units = inspect_formula_and_units(uli)
    visuals = recommend_visuals_for_text(text)
    experiments = build_experiment_scaffolds(uli)
    exp_signals = experiment_completeness_signals(experiments)

    teaching = {
        "domains_detected": len(domains),
        "diagram_coverage": len(visuals),
        "misconception_annotations": len(misconceptions),
        "unit_consistency": units.get("unit_consistency"),
        "formula_consistency": units.get("formula_consistency"),
        "experiment_completeness": exp_signals.get("completeness"),
        "concept_sequencing": "ok" if domains else "unknown",
        "scientific_accuracy_signal": "pass"
        if units.get("formula_consistency") != "warn" and not units.get("artifact_failed_count")
        else "warn",
    }

    findings_seed: list[dict[str, Any]] = []
    if domains and not visuals:
        findings_seed.append(
            {
                "rule_id": "ULIQE.PHYS.PIP.010",
                "severity": "warning",
                "message": "Physics domains detected but no diagram/visual recommendations produced.",
                "category": "pedagogy",
            }
        )
    if units.get("formula_consistency") == "warn" or units.get("unit_consistency") == "warn":
        findings_seed.append(
            {
                "rule_id": "ULIQE.PHYS.PIP.020",
                "severity": "warning",
                "message": "Formula or unit consistency warning from STEM passthrough / pedagogical checks.",
                "category": "stem_accuracy",
                "evidence": {
                    "formula_consistency": units.get("formula_consistency"),
                    "unit_consistency": units.get("unit_consistency"),
                    "artifact_failed_count": units.get("artifact_failed_count"),
                },
            }
        )
    if exp_signals.get("applicable") and exp_signals.get("completeness") == "template_only":
        findings_seed.append(
            {
                "rule_id": "ULIQE.PHYS.PIP.030",
                "severity": "info",
                "message": "Experiment scaffold present; aim/equipment not fully extractable from source.",
                "category": "pedagogy",
            }
        )
    if domains and misconceptions:
        findings_seed.append(
            {
                "rule_id": "ULIQE.PHYS.PIP.040",
                "severity": "info",
                "message": f"Annotated {len(misconceptions)} potential physics misconception pattern(s).",
                "category": "pedagogy",
            }
        )
    if domains:
        findings_seed.append(
            {
                "rule_id": "ULIQE.PHYS.PIP.000",
                "severity": "info",
                "message": (
                    f"PIP signals: {len(domains)} domain(s), {len(visuals)} diagram(s), "
                    f"formula={units.get('formula_consistency')}, units={units.get('unit_consistency')}."
                ),
                "category": "pedagogy",
            }
        )

    return {
        "domains": domains,
        "misconceptions": misconceptions,
        "units_formulas": units,
        "visuals": visuals,
        "experiments": experiments,
        "experiment_signals": exp_signals,
        "teaching": teaching,
        "findings_seed": findings_seed,
        "provenance": "physics_intelligence.validators",
    }
