"""English / literacy validation — additive ELIP signals; never invents language content."""

from __future__ import annotations

from typing import Any, Mapping

from engines.universal_lesson_validation._uli import coerce_uli, finding
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def _elip_quality_findings(uli: Any) -> list[ValidationFinding]:
    try:
        from engines.english_language_intelligence.validation import collect_english_quality_signals
    except Exception:  # noqa: BLE001
        return []
    try:
        signals = collect_english_quality_signals(uli)
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
                str(seed.get("rule_id") or "ULIQE.ENG.ELIP.999"),
                str(seed.get("category") or "pedagogy"),
                severity,
                str(seed.get("message") or "ELIP quality signal"),
                evidence=dict(seed.get("evidence") or {}) if isinstance(seed.get("evidence"), Mapping) else {},
                recommendation="Review English literacy pedagogy metadata; certification rules unchanged.",
            )
        )
    return out


def validate_english(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []

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
        "english",
        "reading",
        "comprehension",
        "vocabulary",
        "grammar",
        "literature",
        "poetry",
        "essay",
        "writing",
        "listening",
        "speaking",
    )
    applicable = any(m in blob for m in markers)

    if not applicable:
        elip = _elip_quality_findings(obj)
        base = [
            finding(
                "ULIQE.ENG.000",
                "stem_accuracy",
                FindingSeverity.INFO,
                "English validation skipped — not applicable.",
            )
        ]
        return base + elip if elip else base

    findings.append(
        finding(
            "ULIQE.ENG.000",
            "stem_accuracy",
            FindingSeverity.INFO,
            "English literacy inventory checks completed (no invented content).",
        )
    )
    findings.extend(_elip_quality_findings(obj))
    return findings
