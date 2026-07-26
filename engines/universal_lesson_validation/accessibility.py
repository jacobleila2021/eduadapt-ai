"""Accessibility validation against ULI accessibility_structure (report gaps; no invention)."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation._uli import coerce_uli, finding
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def validate_accessibility(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    a11y = obj.accessibility_structure()

    if not a11y.get("reading_level"):
        findings.append(
            finding(
                "ULIQE.A11Y.001",
                "accessibility",
                FindingSeverity.ERROR,
                "Reading level metadata missing.",
                field_path="accessibility_structure.reading_level",
            )
        )
    else:
        findings.append(
            finding(
                "ULIQE.A11Y.001",
                "accessibility",
                FindingSeverity.INFO,
                "Reading level / difficulty heuristic present on ULI.",
                evidence={"reading_level": a11y.get("reading_level")},
            )
        )

    for rule_id, label, path in (
        ("ULIQE.A11Y.010", "WCAG 2.2 AA checklist metadata", "accessibility_structure.wcag"),
        ("ULIQE.A11Y.011", "UDL metadata", "accessibility_structure.udl"),
        ("ULIQE.A11Y.012", "Dyslexia support metadata", "accessibility_structure.dyslexia"),
        ("ULIQE.A11Y.013", "Multilingual metadata", "accessibility_structure.multilingual"),
        ("ULIQE.A11Y.014", "Narration metadata", "accessibility_structure.narration"),
        ("ULIQE.A11Y.015", "Executive function demand markers", "accessibility_structure.executive_function_demands"),
    ):
        findings.append(
            finding(
                rule_id,
                "accessibility",
                FindingSeverity.WARNING,
                f"{label} not present on current ULI facade.",
                field_path=path,
                recommendation="Populate via AIE presentation DTO in a later milestone; do not invent.",
            )
        )

    if not a11y.get("language") or a11y.get("language") == "unknown":
        findings.append(
            finding(
                "ULIQE.A11Y.020",
                "accessibility",
                FindingSeverity.WARNING,
                "Language is unknown — multilingual/narration routing limited.",
                field_path="accessibility_structure.language",
            )
        )

    return findings
