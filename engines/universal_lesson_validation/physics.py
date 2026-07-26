"""Physics STEM validation — diagrams/forces artifacts; never invents diagrams."""

from __future__ import annotations

from typing import Any, Mapping

from engines.types import ValidationStatus
from engines.universal_lesson_validation._uli import coerce_uli, finding, stem_applicable
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def _pip_quality_findings(uli: Any) -> list[ValidationFinding]:
    """
    Additive PIP pedagogy / integrity signals.

    Does not alter ULIQE scoring weights or certification thresholds — emits
    INFO/WARNING findings only.
    """
    try:
        from engines.physics_intelligence.validators import collect_physics_quality_signals
    except Exception:  # noqa: BLE001
        return []
    try:
        signals = collect_physics_quality_signals(uli)
    except Exception:  # noqa: BLE001
        return []

    out: list[ValidationFinding] = []
    for seed in signals.get("findings_seed") or []:
        if not isinstance(seed, Mapping):
            continue
        sev_raw = str(seed.get("severity") or "info").lower()
        severity = {
            "info": FindingSeverity.INFO,
            "warning": FindingSeverity.WARNING,
            "error": FindingSeverity.WARNING,
            "critical": FindingSeverity.WARNING,
        }.get(sev_raw, FindingSeverity.INFO)
        out.append(
            finding(
                str(seed.get("rule_id") or "ULIQE.PHYS.PIP.999"),
                str(seed.get("category") or "pedagogy"),
                severity,
                str(seed.get("message") or "PIP quality signal"),
                evidence=dict(seed.get("evidence") or {}) if isinstance(seed.get("evidence"), Mapping) else {},
                recommendation="Review physics pedagogy metadata; curriculum certification rules unchanged.",
            )
        )
    return out


def validate_physics(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    stem = obj.stem_structure()
    phys_claims = list(stem.get("scientific_calculations") or [])
    artifacts = [a for a in (stem.get("artifacts") or []) if isinstance(a, Mapping)]
    phys_artifacts = [
        a
        for a in artifacts
        if str(a.get("engine_id") or "") in {"sympy_force", "physics_diagram"}
        or "physics" in str(a.get("task_kind") or "").lower()
        or "force" in str(a.get("task_kind") or "").lower()
    ]

    if not phys_claims and not phys_artifacts:
        pip_findings = _pip_quality_findings(obj)
        base = [
            finding(
                "ULIQE.PHYS.000",
                "stem_accuracy",
                FindingSeverity.INFO,
                "Physics validation skipped — not applicable."
                if not stem_applicable(obj)
                else "STEM present but no physics claims/artifacts on ULI passthrough.",
            )
        ]
        return base + pip_findings

    for art in phys_artifacts:
        if art.get("ok") is False or str(art.get("validation") or "") == ValidationStatus.FAIL.value:
            findings.append(
                finding(
                    "ULIQE.PHYS.010",
                    "stem_accuracy",
                    FindingSeverity.ERROR,
                    f"Physics artifact failed: {art.get('engine_id')}",
                    evidence={"engine_id": art.get("engine_id")},
                )
            )

    for warning in stem.get("routing_warnings") or []:
        findings.append(
            finding(
                "ULIQE.PHYS.020",
                "stem_accuracy",
                FindingSeverity.WARNING,
                f"STEM routing warning: {warning}",
            )
        )

    if not findings:
        findings.append(
            finding(
                "ULIQE.PHYS.000",
                "stem_accuracy",
                FindingSeverity.INFO,
                f"Physics checks OK ({len(phys_claims)} claims, {len(phys_artifacts)} artifacts).",
            )
        )
    findings.extend(_pip_quality_findings(obj))
    return findings
