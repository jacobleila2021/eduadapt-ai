"""Mathematics quality signals for ULIQE — additive findings only; never change certify rules."""

from __future__ import annotations

from typing import Any, Mapping

from engines.mathematics_intelligence.domains import detect_domains
from engines.mathematics_intelligence.misconceptions import detect_math_misconceptions
from engines.mathematics_intelligence.symbolic import inspect_symbolic_consistency
from engines.mathematics_intelligence.visualizations import recommend_visuals_for_text


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


def collect_math_quality_signals(uli: Any) -> dict[str, Any]:
    """
    Return structured pedagogy / integrity signals.

    Consumers (ULIQE mathematics stage) may emit INFO/WARNING findings from these
    without altering score weights or certification thresholds.
    """
    text = _source_text(uli)
    domains = detect_domains(text)
    misconceptions = detect_math_misconceptions(text)
    symbolic = inspect_symbolic_consistency(uli)
    visuals = recommend_visuals_for_text(text)

    teaching = {
        "domains_detected": len(domains),
        "representation_coverage": len(visuals),
        "misconception_annotations": len(misconceptions),
        "symbol_consistency": symbolic.get("symbol_consistency"),
        "pedagogical_completeness": "partial" if domains else "unknown",
    }

    findings_seed: list[dict[str, Any]] = []
    if domains and not visuals:
        findings_seed.append(
            {
                "rule_id": "ULIQE.MATH.MIP.010",
                "severity": "warning",
                "message": "Mathematics domains detected but no visual representation recommendations produced.",
                "category": "pedagogy",
            }
        )
    if symbolic.get("symbol_consistency") == "warn":
        findings_seed.append(
            {
                "rule_id": "ULIQE.MATH.MIP.020",
                "severity": "warning",
                "message": "Symbolic consistency warning from Computation Layer artifacts or parse checks.",
                "category": "stem_accuracy",
                "evidence": {
                    "artifact_failed_count": symbolic.get("artifact_failed_count"),
                    "parse_fail_count": sum(1 for p in symbolic.get("parse_checks") or [] if not p.get("ok")),
                },
            }
        )
    if domains and misconceptions:
        findings_seed.append(
            {
                "rule_id": "ULIQE.MATH.MIP.030",
                "severity": "info",
                "message": f"Annotated {len(misconceptions)} potential misconception pattern(s) for tutoring.",
                "category": "pedagogy",
            }
        )
    if domains:
        findings_seed.append(
            {
                "rule_id": "ULIQE.MATH.MIP.000",
                "severity": "info",
                "message": (
                    f"MIP signals: {len(domains)} domain(s), {len(visuals)} visual(s), "
                    f"symbol={symbolic.get('symbol_consistency')}."
                ),
                "category": "pedagogy",
            }
        )

    return {
        "domains": domains,
        "misconceptions": misconceptions,
        "symbolic": symbolic,
        "visuals": visuals,
        "teaching": teaching,
        "findings_seed": findings_seed,
        "provenance": "mathematics_intelligence.validators",
    }
