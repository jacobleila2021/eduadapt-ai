"""Schema-stage checks for ULIQE (malformed object rejection)."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation._uli import coerce_uli, finding
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def validate_schema(uli: Any) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    try:
        obj = coerce_uli(uli)
    except (TypeError, ValueError) as exc:
        return [
            finding(
                "ULIQE.SCHEMA.001",
                "schema",
                FindingSeverity.CRITICAL,
                f"Malformed ULI object: {exc}",
                recommendation="Pass UniversalLessonIntelligence or a full to_dict() snapshot.",
            )
        ]

    if not obj.source_id:
        findings.append(
            finding(
                "ULIQE.SCHEMA.002",
                "schema",
                FindingSeverity.ERROR,
                "Missing source_id on ULI profile/envelope.",
                field_path="source_id",
                recommendation="Ensure SourceDocumentEnvelope.source_id is populated at ingest.",
            )
        )

    profile = obj.universal_profile
    for key in ("schema_version", "title", "topic", "claim_ledger", "language"):
        if key not in profile or profile.get(key) in (None, ""):
            findings.append(
                finding(
                    "ULIQE.SCHEMA.003",
                    "schema",
                    FindingSeverity.ERROR,
                    f"Required profile field missing or empty: {key}",
                    field_path=f"universal_profile.{key}",
                )
            )

    claim_ids: list[str] = []
    for claim in list(profile.get("claim_ledger") or []):
        if not isinstance(claim, dict):
            findings.append(
                finding(
                    "ULIQE.SCHEMA.004",
                    "schema",
                    FindingSeverity.ERROR,
                    "Claim ledger entries must be mappings.",
                    field_path="universal_profile.claim_ledger",
                )
            )
            continue
        cid = claim.get("claim_id")
        if not cid:
            findings.append(
                finding(
                    "ULIQE.SCHEMA.004",
                    "schema",
                    FindingSeverity.ERROR,
                    "Claim missing claim_id.",
                    field_path="universal_profile.claim_ledger",
                )
            )
        else:
            claim_ids.append(str(cid))
    if len(claim_ids) != len(set(claim_ids)):
        findings.append(
            finding(
                "ULIQE.SCHEMA.004",
                "schema",
                FindingSeverity.ERROR,
                "Duplicate claim_id values in claim_ledger.",
                field_path="universal_profile.claim_ledger",
            )
        )

    envelope = obj.source_envelope
    if not envelope.get("source_hash") and not envelope.get("blocks"):
        findings.append(
            finding(
                "ULIQE.SCHEMA.005",
                "schema",
                FindingSeverity.WARNING,
                "Envelope lacks source_hash and blocks — provenance weak.",
                field_path="source_envelope",
                recommendation="Re-ingest through universal_ingest.",
            )
        )

    if not any(f.severity in (FindingSeverity.ERROR, FindingSeverity.CRITICAL) for f in findings):
        findings.append(
            finding(
                "ULIQE.SCHEMA.000",
                "schema",
                FindingSeverity.INFO,
                "ULI schema structure accepted.",
                evidence={"source_id": obj.source_id, "uli_schema": obj.schema_version},
            )
        )
    return findings
