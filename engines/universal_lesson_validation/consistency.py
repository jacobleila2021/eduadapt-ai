"""Internal consistency checks across ULI semantic layers."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation._uli import coerce_uli, finding
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def validate_consistency(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    edu = obj.educational_structure()
    profile = obj.universal_profile

    if edu.get("title") and profile.get("title") and edu["title"] != profile.get("title"):
        findings.append(
            finding(
                "ULIQE.CONS.001",
                "consistency",
                FindingSeverity.ERROR,
                "educational_structure.title does not match universal_profile.title.",
                field_path="educational_structure.title",
            )
        )

    if edu.get("topic") and profile.get("topic") and edu["topic"] != profile.get("topic"):
        findings.append(
            finding(
                "ULIQE.CONS.002",
                "consistency",
                FindingSeverity.ERROR,
                "educational_structure.topic does not match universal_profile.topic.",
                field_path="educational_structure.topic",
            )
        )

    lang_edu = edu.get("language")
    lang_prof = profile.get("language")
    if lang_edu and lang_prof and lang_edu != lang_prof:
        findings.append(
            finding(
                "ULIQE.CONS.003",
                "consistency",
                FindingSeverity.WARNING,
                "Language mismatch between educational_structure and profile.",
                field_path="educational_structure.language",
            )
        )

    # Vocabulary terms should appear somewhere in claim text when both exist.
    vocab = obj.learning_structure().get("vocabulary") or []
    ledger_text = " ".join(
        str(c.get("text") or "").lower()
        for c in (profile.get("claim_ledger") or [])
        if isinstance(c, dict)
    )
    if vocab and ledger_text:
        orphans = []
        for row in vocab[:15]:
            term = str((row or {}).get("term") or "").lower()
            if term and term not in ledger_text:
                orphans.append(term)
        if orphans:
            findings.append(
                finding(
                    "ULIQE.CONS.010",
                    "consistency",
                    FindingSeverity.WARNING,
                    f"{len(orphans)} vocabulary term(s) not found in claim ledger text.",
                    field_path="learning_structure.vocabulary",
                    evidence={"terms": orphans[:8]},
                    recommendation="Review extraction frequency heuristics; do not invent definitions.",
                )
            )

    if not findings:
        findings.append(
            finding(
                "ULIQE.CONS.000",
                "consistency",
                FindingSeverity.INFO,
                "No internal consistency errors detected.",
            )
        )
    return findings
