"""Biology quality signals for ULIQE — additive findings only."""

from __future__ import annotations

from typing import Any, Mapping

from engines.biology_intelligence.diagrams import (
    diagram_completeness_signals,
    recommend_visuals_for_text,
)
from engines.biology_intelligence.domains import detect_domains
from engines.biology_intelligence.laboratory import (
    build_laboratory_scaffolds,
    laboratory_completeness_signals,
)
from engines.biology_intelligence.misconceptions import detect_biology_misconceptions
from engines.biology_intelligence.processes import build_process_metadata
from engines.biology_intelligence.terminology import inspect_terminology_and_taxonomy


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


def collect_biology_quality_signals(uli: Any) -> dict[str, Any]:
    text = _source_text(uli)
    domains = detect_domains(text)
    misconceptions = detect_biology_misconceptions(text)
    terminology = inspect_terminology_and_taxonomy(uli)
    visuals = recommend_visuals_for_text(text)
    diagram_signals = diagram_completeness_signals(visuals, domains)
    processes = build_process_metadata(text, domains)
    labs = build_laboratory_scaffolds(uli)
    lab_signals = laboratory_completeness_signals(labs)

    teaching = {
        "domains_detected": len(domains),
        "diagram_coverage": len(visuals),
        "diagram_completeness": diagram_signals.get("completeness"),
        "process_count": len(processes.get("processes") or []),
        "process_completeness": "ok" if processes.get("processes") else ("n/a" if not domains else "minimal"),
        "misconception_annotations": len(misconceptions),
        "terminology_consistency": terminology.get("terminology_consistency"),
        "taxonomy_consistency": terminology.get("taxonomy_consistency"),
        "laboratory_completeness": lab_signals.get("completeness"),
        "accessibility_completeness": "ok",  # BIP always emits a11y guidance when analysed
    }

    findings_seed: list[dict[str, Any]] = []
    if domains and diagram_signals.get("completeness") == "missing":
        findings_seed.append(
            {
                "rule_id": "ULIQE.BIO.BIP.010",
                "severity": "warning",
                "message": "Biology domains detected but diagram recommendations empty.",
                "category": "pedagogy",
            }
        )
    if terminology.get("terminology_consistency") == "warn":
        findings_seed.append(
            {
                "rule_id": "ULIQE.BIO.BIP.020",
                "severity": "warning",
                "message": "Biological terminology consistency warning on ULI passthrough.",
                "category": "stem_accuracy",
            }
        )
    if domains and not (processes.get("processes") or []):
        findings_seed.append(
            {
                "rule_id": "ULIQE.BIO.BIP.025",
                "severity": "info",
                "message": "Biology domains present but process metadata is minimal.",
                "category": "pedagogy",
            }
        )
    if lab_signals.get("applicable") and lab_signals.get("completeness") == "template_only":
        findings_seed.append(
            {
                "rule_id": "ULIQE.BIO.BIP.030",
                "severity": "info",
                "message": "Laboratory scaffold present; aim/equipment not fully extractable from source.",
                "category": "pedagogy",
            }
        )
    if domains and misconceptions:
        findings_seed.append(
            {
                "rule_id": "ULIQE.BIO.BIP.040",
                "severity": "info",
                "message": f"Annotated {len(misconceptions)} potential biology misconception pattern(s).",
                "category": "pedagogy",
            }
        )
    if domains:
        findings_seed.append(
            {
                "rule_id": "ULIQE.BIO.BIP.000",
                "severity": "info",
                "message": (
                    f"BIP signals: {len(domains)} domain(s), {len(visuals)} diagram(s), "
                    f"processes={len(processes.get('processes') or [])}, "
                    f"lab={lab_signals.get('completeness')}."
                ),
                "category": "pedagogy",
            }
        )

    return {
        "domains": domains,
        "misconceptions": misconceptions,
        "terminology": terminology,
        "visuals": visuals,
        "diagram_signals": diagram_signals,
        "processes": processes,
        "laboratory": labs,
        "laboratory_signals": lab_signals,
        "teaching": teaching,
        "findings_seed": findings_seed,
        "provenance": "biology_intelligence.validators",
    }
