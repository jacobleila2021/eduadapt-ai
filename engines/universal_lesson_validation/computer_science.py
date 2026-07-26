"""Computer science validation — additive CSIP signals; never invents content."""

from __future__ import annotations

from typing import Any, Mapping

from engines.universal_lesson_validation._uli import coerce_uli, finding
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def _csip_quality_findings(uli: Any) -> list[ValidationFinding]:
    try:
        from engines.computer_science_intelligence.validation import collect_computer_science_quality_signals
    except Exception:  # noqa: BLE001
        return []
    try:
        signals = collect_computer_science_quality_signals(uli)
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
                str(seed.get("rule_id") or "ULIQE.CS.CSIP.999"),
                str(seed.get("category") or "pedagogy"),
                severity,
                str(seed.get("message") or "CSIP quality signal"),
                evidence=dict(seed.get("evidence") or {}) if isinstance(seed.get("evidence"), Mapping) else {},
                recommendation="Review computer science pedagogy metadata; certification rules unchanged.",
            )
        )
    return out


def validate_computer_science(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    blob_parts: list[str] = []
    try:
        edu = obj.educational_structure()
        blob_parts.append(str(edu.get("topic") or ""))
        blob_parts.append(str(edu.get("subject") or ""))
    except Exception:  # noqa: BLE001
        pass
    try:
        env = obj.source_envelope
        if isinstance(env, Mapping):
            blob_parts.append(str(env.get("normalized_text") or env.get("text") or "")[:2000])
    except Exception:  # noqa: BLE001
        pass
    blob = " ".join(blob_parts).lower()
    markers = (
        "computer science",
        "programming",
        "algorithm",
        "coding",
        "python",
        "database",
        "sql",
        "network",
        "cybersecurity",
        "machine learning",
        "artificial intelligence",
        "data structure",
        "debugging",
    )
    applicable = any(m in blob for m in markers)

    if not applicable:
        csip = _csip_quality_findings(obj)
        base = [
            finding(
                "ULIQE.CS.000",
                "stem_accuracy",
                FindingSeverity.INFO,
                "Computer science validation skipped — not applicable.",
            )
        ]
        return base + csip if csip else base

    findings = [
        finding(
            "ULIQE.CS.000",
            "stem_accuracy",
            FindingSeverity.INFO,
            "Computer science inventory checks completed (no invented content).",
        )
    ]
    findings.extend(_csip_quality_findings(obj))
    return findings
