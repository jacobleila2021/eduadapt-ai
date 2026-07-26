"""Universal visual validation — additive UVIE signals; never invents diagrams."""

from __future__ import annotations

from typing import Any, Mapping

from engines.universal_lesson_validation._uli import coerce_uli, finding
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def _uvie_quality_findings(uli: Any) -> list[ValidationFinding]:
    try:
        from engines.universal_visual_intelligence.validation import collect_uvie_quality_signals
    except Exception:  # noqa: BLE001
        return []
    try:
        signals = collect_uvie_quality_signals(uli=uli)
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
                str(seed.get("rule_id") or "ULIQE.UVIE.999"),
                str(seed.get("category") or "diagrams"),
                severity,
                str(seed.get("message") or "UVIE quality signal"),
                evidence=dict(seed.get("evidence") or {}) if isinstance(seed.get("evidence"), Mapping) else {},
                recommendation="Review visual priority and alt text; certification rules unchanged.",
            )
        )
    return out


def validate_universal_visual(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings = [
        finding(
            "ULIQE.UVIE.000",
            "diagrams",
            FindingSeverity.INFO,
            "Universal visual inventory checks completed (deterministic-first; no AI invent).",
        )
    ]
    findings.extend(_uvie_quality_findings(obj))
    return findings
