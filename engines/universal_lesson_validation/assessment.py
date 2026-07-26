"""Assessment coverage validation — maps objectives to opportunities when both exist."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation._uli import coerce_uli, finding, nonempty_list
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def validate_assessment(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    learn = obj.learning_structure()
    assess = obj.assessment_structure()
    objectives = list(learn.get("learning_objectives") or [])
    opportunities = list(assess.get("assessment_opportunities") or [])
    misconceptions = list(learn.get("misconceptions") or [])

    if not nonempty_list(opportunities):
        findings.append(
            finding(
                "ULIQE.ASM.001",
                "assessment_coverage",
                FindingSeverity.WARNING,
                "No assessment opportunities on ULI.",
                field_path="assessment_structure.assessment_opportunities",
            )
        )
    else:
        findings.append(
            finding(
                "ULIQE.ASM.001",
                "assessment_coverage",
                FindingSeverity.INFO,
                f"{len(opportunities)} assessment opportunity(ies) present.",
            )
        )

    if objectives and not opportunities:
        findings.append(
            finding(
                "ULIQE.ASM.010",
                "assessment_coverage",
                FindingSeverity.ERROR,
                "Learning objectives exist but no assessments map to them.",
                recommendation="Extract or author assessments linked to objectives; do not invent questions here.",
            )
        )

    # Answer keys / formative vs summative not on ULI — gaps only.
    findings.append(
        finding(
            "ULIQE.ASM.020",
            "assessment_coverage",
            FindingSeverity.WARNING,
            "Formative/summative split and answer keys are not present on ULI facade.",
            recommendation="AME / worksheet generation owns keys after teaching; ULIQE only certifies ULI inventory.",
        )
    )

    if misconceptions and not opportunities:
        findings.append(
            finding(
                "ULIQE.ASM.030",
                "assessment_coverage",
                FindingSeverity.WARNING,
                "Misconceptions listed without assessment opportunities for probing them.",
            )
        )

    if objectives and opportunities:
        # Soft lexical overlap check — report weak coverage, never invent mappings.
        obj_text = " ".join(str(o) for o in objectives).lower()
        hit = 0
        for q in opportunities:
            qtext = str((q or {}).get("question") or q).lower()
            if any(tok in qtext for tok in obj_text.split() if len(tok) > 5):
                hit += 1
        ratio = hit / max(len(opportunities), 1)
        if ratio < 0.2:
            findings.append(
                finding(
                    "ULIQE.ASM.040",
                    "assessment_coverage",
                    FindingSeverity.WARNING,
                    "Low lexical overlap between objectives and assessment opportunities.",
                    evidence={"overlap_ratio": round(ratio, 2)},
                )
            )

    return findings
