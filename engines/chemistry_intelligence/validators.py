"""Chemistry quality signals for ULIQE — additive findings only."""

from __future__ import annotations

from typing import Any, Mapping

from engines.chemistry_intelligence.domains import detect_domains
from engines.chemistry_intelligence.equations import inspect_equations_and_notation
from engines.chemistry_intelligence.laboratory import (
    build_laboratory_scaffolds,
    laboratory_completeness_signals,
)
from engines.chemistry_intelligence.misconceptions import detect_chemistry_misconceptions
from engines.chemistry_intelligence.molecular_models import build_molecular_metadata
from engines.chemistry_intelligence.diagrams import recommend_visuals_for_text


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


def collect_chemistry_quality_signals(uli: Any) -> dict[str, Any]:
    text = _source_text(uli)
    domains = detect_domains(text)
    misconceptions = detect_chemistry_misconceptions(text)
    equations = inspect_equations_and_notation(uli)
    molecular = build_molecular_metadata(text, domains)
    visuals = recommend_visuals_for_text(text)
    labs = build_laboratory_scaffolds(uli)
    lab_signals = laboratory_completeness_signals(labs)

    teaching = {
        "domains_detected": len(domains),
        "diagram_coverage": len(visuals),
        "misconception_annotations": len(misconceptions),
        "formula_validation": equations.get("formula_validation"),
        "balancing_signal": equations.get("balancing_signal"),
        "notation_consistency": equations.get("notation_consistency"),
        "laboratory_completeness": lab_signals.get("completeness"),
        "safety_metadata": lab_signals.get("safety_metadata"),
        "molecular_representation": "ok" if molecular.get("representation_hooks") else "minimal",
    }

    findings_seed: list[dict[str, Any]] = []
    if domains and not visuals:
        findings_seed.append(
            {
                "rule_id": "ULIQE.CHEM.CIP.010",
                "severity": "warning",
                "message": "Chemistry domains detected but no diagram/visual recommendations produced.",
                "category": "pedagogy",
            }
        )
    if equations.get("balancing_signal") == "warn" or equations.get("formula_validation") == "warn":
        findings_seed.append(
            {
                "rule_id": "ULIQE.CHEM.CIP.020",
                "severity": "warning",
                "message": "Equation balancing / formula validation warning from Computation Layer artifacts.",
                "category": "stem_accuracy",
                "evidence": {
                    "balancing_signal": equations.get("balancing_signal"),
                    "artifact_failed_count": equations.get("artifact_failed_count"),
                },
            }
        )
    if equations.get("notation_consistency") == "warn":
        findings_seed.append(
            {
                "rule_id": "ULIQE.CHEM.CIP.025",
                "severity": "warning",
                "message": "Chemical notation consistency warning (missing raw equation text).",
                "category": "stem_accuracy",
            }
        )
    if lab_signals.get("applicable") and lab_signals.get("completeness") == "template_only":
        findings_seed.append(
            {
                "rule_id": "ULIQE.CHEM.CIP.030",
                "severity": "info",
                "message": "Laboratory scaffold present; aim/equipment not fully extractable from source.",
                "category": "pedagogy",
            }
        )
    if lab_signals.get("applicable") and lab_signals.get("safety_metadata") == "missing":
        findings_seed.append(
            {
                "rule_id": "ULIQE.CHEM.CIP.035",
                "severity": "warning",
                "message": "Laboratory scaffold missing safety metadata.",
                "category": "pedagogy",
            }
        )
    if domains and misconceptions:
        findings_seed.append(
            {
                "rule_id": "ULIQE.CHEM.CIP.040",
                "severity": "info",
                "message": f"Annotated {len(misconceptions)} potential chemistry misconception pattern(s).",
                "category": "pedagogy",
            }
        )
    if domains:
        findings_seed.append(
            {
                "rule_id": "ULIQE.CHEM.CIP.000",
                "severity": "info",
                "message": (
                    f"CIP signals: {len(domains)} domain(s), {len(visuals)} diagram(s), "
                    f"balance={equations.get('balancing_signal')}, "
                    f"lab={lab_signals.get('completeness')}."
                ),
                "category": "pedagogy",
            }
        )

    return {
        "domains": domains,
        "misconceptions": misconceptions,
        "equations": equations,
        "molecular": molecular,
        "visuals": visuals,
        "laboratory": labs,
        "laboratory_signals": lab_signals,
        "teaching": teaching,
        "findings_seed": findings_seed,
        "provenance": "chemistry_intelligence.validators",
    }
