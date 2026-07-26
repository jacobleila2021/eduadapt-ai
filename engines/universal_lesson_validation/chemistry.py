"""Chemistry STEM validation — atom-count / balancer artifacts only; never invents equations."""

from __future__ import annotations

from typing import Any, Mapping

from engines.types import ValidationStatus
from engines.universal_lesson_validation._uli import coerce_uli, finding, stem_applicable
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def _cip_quality_findings(uli: Any) -> list[ValidationFinding]:
    """Additive CIP pedagogy / integrity signals — INFO/WARNING only."""
    try:
        from engines.chemistry_intelligence.validators import collect_chemistry_quality_signals
    except Exception:  # noqa: BLE001
        return []
    try:
        signals = collect_chemistry_quality_signals(uli)
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
                str(seed.get("rule_id") or "ULIQE.CHEM.CIP.999"),
                str(seed.get("category") or "pedagogy"),
                severity,
                str(seed.get("message") or "CIP quality signal"),
                evidence=dict(seed.get("evidence") or {}) if isinstance(seed.get("evidence"), Mapping) else {},
                recommendation="Review chemistry pedagogy metadata; curriculum certification rules unchanged.",
            )
        )
    return out


def validate_chemistry(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    stem = obj.stem_structure()
    chem_claims = list(stem.get("chemical_equations") or [])
    artifacts = [a for a in (stem.get("artifacts") or []) if isinstance(a, Mapping)]
    chem_artifacts = [
        a
        for a in artifacts
        if str(a.get("engine_id") or "") in {"chemistry_balancer", "chempy", "mhchem", "rdkit"}
        or "chem" in str(a.get("task_kind") or "").lower()
    ]

    if not chem_claims and not chem_artifacts:
        cip = _cip_quality_findings(obj)
        base = [
            finding(
                "ULIQE.CHEM.000",
                "stem_accuracy",
                FindingSeverity.INFO,
                "Chemistry validation skipped — not applicable."
                if not stem_applicable(obj)
                else "STEM present but no chemistry claims/artifacts on ULI passthrough.",
            )
        ]
        return base + cip

    for i, claim in enumerate(chem_claims):
        if isinstance(claim, Mapping) and not claim.get("raw"):
            findings.append(
                finding(
                    "ULIQE.CHEM.001",
                    "stem_accuracy",
                    FindingSeverity.WARNING,
                    f"Chemical claim[{i}] missing raw equation text.",
                )
            )

    for art in chem_artifacts:
        if art.get("ok") is False or str(art.get("validation") or "") == ValidationStatus.FAIL.value:
            findings.append(
                finding(
                    "ULIQE.CHEM.010",
                    "stem_accuracy",
                    FindingSeverity.CRITICAL,
                    f"Chemistry artifact failed validation: {art.get('engine_id')}",
                    recommendation="Require atom-count validated balancer output before downstream use.",
                    evidence={"engine_id": art.get("engine_id"), "detail": art.get("validation_detail") or art.get("error")},
                )
            )
        exact = art.get("exact")
        if exact is None and art.get("ok"):
            findings.append(
                finding(
                    "ULIQE.CHEM.011",
                    "stem_accuracy",
                    FindingSeverity.WARNING,
                    f"Chemistry artifact {art.get('engine_id')} has no exact payload for provenance.",
                )
            )

    if not findings:
        findings.append(
            finding(
                "ULIQE.CHEM.000",
                "stem_accuracy",
                FindingSeverity.INFO,
                f"Chemistry checks OK ({len(chem_claims)} claims, {len(chem_artifacts)} artifacts).",
            )
        )
    findings.extend(_cip_quality_findings(obj))
    return findings
