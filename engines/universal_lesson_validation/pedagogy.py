"""Pedagogical validation — sequence, scaffolding signals, age band (report only)."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation._uli import coerce_uli, finding, nonempty_list
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def validate_pedagogy(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    learn = obj.learning_structure()
    a11y = obj.accessibility_structure()
    resources = obj.learning_resources()
    assess = obj.assessment_structure()

    if not nonempty_list(learn.get("learning_objectives")):
        findings.append(
            finding(
                "ULIQE.PED.001",
                "pedagogy",
                FindingSeverity.ERROR,
                "No learning objectives — instructional intent unclear.",
                field_path="learning_structure.learning_objectives",
            )
        )

    if not nonempty_list(learn.get("key_concepts")):
        findings.append(
            finding(
                "ULIQE.PED.002",
                "pedagogy",
                FindingSeverity.WARNING,
                "No key concepts extracted for instructional sequencing.",
                field_path="learning_structure.key_concepts",
            )
        )

    examples = resources.get("worked_examples") or []
    activities_proxy = examples  # ULI has no separate activities yet
    if not activities_proxy:
        findings.append(
            finding(
                "ULIQE.PED.010",
                "pedagogy",
                FindingSeverity.WARNING,
                "No worked examples/activities detected — activity balance cannot be verified.",
                field_path="learning_resources.worked_examples",
            )
        )

    if not nonempty_list(assess.get("assessment_opportunities")):
        findings.append(
            finding(
                "ULIQE.PED.011",
                "pedagogy",
                FindingSeverity.WARNING,
                "No review/assessment questions — revision opportunities thin.",
                field_path="assessment_structure.assessment_opportunities",
            )
        )

    difficulty = a11y.get("reading_level") or {}
    age = a11y.get("age_estimate") or {}
    if difficulty.get("band") and age.get("band"):
        findings.append(
            finding(
                "ULIQE.PED.020",
                "pedagogy",
                FindingSeverity.INFO,
                f"Age/difficulty heuristics present: difficulty={difficulty.get('band')}, age={age.get('band')}",
                evidence={"difficulty": difficulty, "age_estimate": age},
            )
        )
    else:
        findings.append(
            finding(
                "ULIQE.PED.021",
                "pedagogy",
                FindingSeverity.WARNING,
                "Age appropriateness metadata incomplete.",
                field_path="accessibility_structure",
            )
        )

    # Cognitive load / scaffolding / transitions not on ULI — gap only.
    findings.append(
        finding(
            "ULIQE.PED.030",
            "pedagogy",
            FindingSeverity.WARNING,
            "Cognitive load, scaffolding, and transition quality are not encoded on ULI yet.",
            recommendation="Future Pedagogical Intelligence may supply these; ULIQE reports absence only.",
        )
    )

    return findings
