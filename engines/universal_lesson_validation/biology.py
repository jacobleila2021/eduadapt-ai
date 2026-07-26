"""Biology validation — terminology/visual inventory only; never invents biology facts."""

from __future__ import annotations

from typing import Any, Mapping

from engines.universal_lesson_validation._uli import coerce_uli, finding
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def _bip_quality_findings(uli: Any) -> list[ValidationFinding]:
    """Additive BIP pedagogy / integrity signals — INFO/WARNING only."""
    try:
        from engines.biology_intelligence.validators import collect_biology_quality_signals
    except Exception:  # noqa: BLE001
        return []
    try:
        signals = collect_biology_quality_signals(uli)
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
                str(seed.get("rule_id") or "ULIQE.BIO.BIP.999"),
                str(seed.get("category") or "pedagogy"),
                severity,
                str(seed.get("message") or "BIP quality signal"),
                evidence=dict(seed.get("evidence") or {}) if isinstance(seed.get("evidence"), Mapping) else {},
                recommendation="Review biology pedagogy metadata; curriculum certification rules unchanged.",
            )
        )
    return out


def validate_biology(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    stem = obj.stem_structure()
    learn = obj.learning_structure()
    resources = obj.learning_resources()

    bio_terms = list(stem.get("biological_terminology") or [])
    visuals = list(resources.get("diagrams") or [])
    vocab = list(learn.get("vocabulary") or [])

    blob = " ".join(
        [
            str(obj.educational_structure().get("topic") or ""),
            " ".join(str((v or {}).get("term") or "") for v in vocab if isinstance(v, Mapping)),
            str((obj.source_envelope or {}).get("normalized_text") or (obj.source_envelope or {}).get("text") or "")
            if isinstance(obj.source_envelope, Mapping)
            else "",
        ]
    ).lower()
    bio_markers = (
        "cell",
        "photosynthesis",
        "respiration",
        "tissue",
        "organism",
        "enzyme",
        "dna",
        "ecology",
        "biology",
        "mitosis",
        "gene",
    )
    applicable = any(m in blob for m in bio_markers) or bool(bio_terms)

    if not applicable:
        bip = _bip_quality_findings(obj)
        base = [
            finding(
                "ULIQE.BIO.000",
                "stem_accuracy",
                FindingSeverity.INFO,
                "Biology validation skipped — not applicable.",
            )
        ]
        return base + bip if bip else base

    if not vocab and not bio_terms:
        findings.append(
            finding(
                "ULIQE.BIO.001",
                "stem_accuracy",
                FindingSeverity.WARNING,
                "Biology-like topic detected but vocabulary/biological terminology empty.",
                field_path="learning_structure.vocabulary",
            )
        )

    preferred = list(stem.get("preferred_visuals") or [])
    if applicable and not visuals and not preferred:
        findings.append(
            finding(
                "ULIQE.BIO.010",
                "stem_accuracy",
                FindingSeverity.WARNING,
                "No biology diagram/visual inventory on ULI for a biology-like lesson.",
                recommendation="Attach verified visuals via visualization priority; do not invent figures.",
            )
        )

    for art in stem.get("artifacts") or []:
        if not isinstance(art, Mapping):
            continue
        if art.get("ok") is False:
            findings.append(
                finding(
                    "ULIQE.BIO.020",
                    "stem_accuracy",
                    FindingSeverity.ERROR,
                    f"STEM artifact failed while validating biology-like lesson: {art.get('engine_id')}",
                )
            )

    if not findings:
        findings.append(
            finding(
                "ULIQE.BIO.000",
                "stem_accuracy",
                FindingSeverity.INFO,
                "Biology inventory checks completed (no invented content).",
            )
        )
    findings.extend(_bip_quality_findings(obj))
    return findings
