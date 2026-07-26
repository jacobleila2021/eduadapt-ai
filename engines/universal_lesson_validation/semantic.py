"""Semantic integrity — claim ledger, duplicate concepts, orphan refs."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation._uli import coerce_uli, finding, nonempty_list
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def validate_semantic(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    profile = obj.universal_profile
    ledger = [c for c in (profile.get("claim_ledger") or []) if isinstance(c, dict)]
    concepts = list(obj.learning_structure().get("key_concepts") or [])

    if not ledger:
        findings.append(
            finding(
                "ULIQE.SEM.001",
                "semantic_integrity",
                FindingSeverity.CRITICAL,
                "Empty claim ledger — semantic grounding absent.",
                field_path="claim_ledger",
            )
        )
        return findings

    # Duplicate concept labels
    labels = [str((c or {}).get("concept") or "").lower() for c in concepts if isinstance(c, dict)]
    dupes = sorted({x for x in labels if x and labels.count(x) > 1})
    if dupes:
        findings.append(
            finding(
                "ULIQE.SEM.010",
                "semantic_integrity",
                FindingSeverity.WARNING,
                f"Duplicate concept labels: {', '.join(dupes[:8])}",
                field_path="learning_structure.key_concepts",
            )
        )

    # Orphan concepts: no source_refs
    orphans = [
        str(c.get("concept"))
        for c in concepts
        if isinstance(c, dict) and not (c.get("source_refs") or [])
    ]
    if orphans:
        findings.append(
            finding(
                "ULIQE.SEM.011",
                "semantic_integrity",
                FindingSeverity.WARNING,
                f"{len(orphans)} concept(s) lack source_refs.",
                evidence={"concepts": orphans[:10]},
            )
        )

    # Claims without block ids
    unlinked = sum(1 for c in ledger if not (c.get("source_block_ids") or []))
    if unlinked:
        findings.append(
            finding(
                "ULIQE.SEM.012",
                "semantic_integrity",
                FindingSeverity.WARNING,
                f"{unlinked} claim(s) missing source_block_ids.",
                field_path="claim_ledger",
            )
        )

    # Knowledge graph / cross-refs not on ULI
    findings.append(
        finding(
            "ULIQE.SEM.020",
            "semantic_integrity",
            FindingSeverity.INFO,
            "Prerequisite/knowledge-graph links are not first-class on ULI facade (optional CIE later).",
        )
    )

    if nonempty_list(concepts) and ledger:
        findings.append(
            finding(
                "ULIQE.SEM.000",
                "semantic_integrity",
                FindingSeverity.INFO,
                f"Semantic core present: {len(ledger)} claims, {len(concepts)} concepts.",
            )
        )

    return findings
