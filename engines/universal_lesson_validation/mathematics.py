"""Mathematics STEM validation — verifies present artifacts; never invents solutions."""

from __future__ import annotations

from typing import Any, Mapping

from engines.types import ValidationStatus
from engines.universal_lesson_validation._uli import coerce_uli, finding, stem_applicable
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def _mip_quality_findings(uli: Any) -> list[ValidationFinding]:
    """
    Additive MIP pedagogy / integrity signals.

    Does not alter ULIQE scoring weights or certification thresholds — emits
    INFO/WARNING findings only for observability and teaching enrichment QA.
    """
    try:
        from engines.mathematics_intelligence.validators import collect_math_quality_signals
    except Exception:  # noqa: BLE001
        return []
    try:
        signals = collect_math_quality_signals(uli)
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
            "error": FindingSeverity.WARNING,  # MIP never escalates certification via ERROR
            "critical": FindingSeverity.WARNING,
        }.get(sev_raw, FindingSeverity.INFO)
        out.append(
            finding(
                str(seed.get("rule_id") or "ULIQE.MATH.MIP.999"),
                str(seed.get("category") or "pedagogy"),
                severity,
                str(seed.get("message") or "MIP quality signal"),
                evidence=dict(seed.get("evidence") or {}) if isinstance(seed.get("evidence"), Mapping) else {},
                recommendation="Review mathematics pedagogy metadata; curriculum certification rules unchanged.",
            )
        )
    return out


def validate_mathematics(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    stem = obj.stem_structure()
    math_claims = list(stem.get("mathematical_expressions") or [])
    artifacts = [a for a in (stem.get("artifacts") or []) if isinstance(a, Mapping)]

    if not math_claims and not any(
        "math" in str(a.get("task_kind") or a.get("engine_id") or "").lower()
        or str(a.get("engine_id") or "") in {"sympy", "matplotlib", "numpy"}
        for a in artifacts
    ):
        # Still attach additive MIP signals when lesson text looks mathematical.
        mip = _mip_quality_findings(obj)
        if stem_applicable(obj):
            base = [
                finding(
                    "ULIQE.MATH.000",
                    "stem_accuracy",
                    FindingSeverity.INFO,
                    "STEM present but no mathematics claims/artifacts on ULI passthrough.",
                )
            ]
            return base + mip
        if mip:
            return mip
        return [
            finding(
                "ULIQE.MATH.000",
                "stem_accuracy",
                FindingSeverity.INFO,
                "Mathematics validation skipped — not applicable.",
            )
        ]

    for i, claim in enumerate(math_claims):
        if not isinstance(claim, Mapping):
            continue
        if not claim.get("raw"):
            findings.append(
                finding(
                    "ULIQE.MATH.001",
                    "stem_accuracy",
                    FindingSeverity.WARNING,
                    f"Math claim[{i}] missing raw expression.",
                    field_path=f"stem_structure.mathematical_expressions[{i}]",
                )
            )

    math_artifacts = [
        a
        for a in artifacts
        if str(a.get("engine_id") or "") in {"sympy", "matplotlib", "numpy", "numpy_scipy"}
        or "math" in str(a.get("task_kind") or "").lower()
    ]
    for art in math_artifacts:
        ok = art.get("ok", True)
        validation = str(art.get("validation") or "")
        if ok is False or validation == ValidationStatus.FAIL.value:
            findings.append(
                finding(
                    "ULIQE.MATH.010",
                    "stem_accuracy",
                    FindingSeverity.ERROR,
                    f"Mathematics engine artifact failed: {art.get('engine_id')}",
                    evidence={"artifact": {"engine_id": art.get("engine_id"), "validation": validation}},
                    recommendation="Do not publish unverified math results; fix Computation Layer output.",
                )
            )

    if not findings:
        findings.append(
            finding(
                "ULIQE.MATH.000",
                "stem_accuracy",
                FindingSeverity.INFO,
                f"Mathematics checks passed for {len(math_claims)} claim(s) / {len(math_artifacts)} artifact(s).",
            )
        )
    findings.extend(_mip_quality_findings(obj))
    return findings
