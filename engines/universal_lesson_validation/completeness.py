"""Completeness validation — flag missing educational elements (never invent)."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation._uli import coerce_uli, finding, nonempty_list
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding

# Ideal ULI completeness checklist. Missing → warning/error, never filled by ULIQE.
_REQUIRED_SOFT = (
    ("title", "educational_structure.title", "title"),
    ("learning_objectives", "learning_structure.learning_objectives", "learning objectives"),
    ("key_concepts", "learning_structure.key_concepts", "concepts"),
    ("vocabulary", "learning_structure.vocabulary", "vocabulary"),
)

_OPTIONAL_INVENTORY = (
    ("definitions", "learning_structure.definitions", "definitions / glossary entries"),
    ("prior_knowledge", "learning_structure.prior_knowledge", "prerequisites / prior knowledge"),
    ("misconceptions", "learning_structure.misconceptions", "misconceptions"),
    ("worked_examples", "learning_resources.worked_examples", "worked examples"),
    ("skills", "learning_structure.skills", "competencies / skills"),
)


def validate_completeness(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    edu = obj.educational_structure()
    learn = obj.learning_structure()
    resources = obj.learning_resources()
    assess = obj.assessment_structure()
    a11y = obj.accessibility_structure()
    findings: list[ValidationFinding] = []

    layers = {
        "educational_structure": edu,
        "learning_structure": learn,
        "learning_resources": resources,
        "assessment_structure": assess,
        "accessibility_structure": a11y,
    }

    def _get(path: str) -> Any:
        section, _, key = path.partition(".")
        return (layers.get(section) or {}).get(key)

    if not str(edu.get("title") or "").strip():
        findings.append(
            finding(
                "ULIQE.COMP.001",
                "completeness",
                FindingSeverity.ERROR,
                "Lesson title is missing.",
                field_path="educational_structure.title",
            )
        )

    # Summary is not a first-class ULI field yet — flag as inventory gap, do not invent.
    findings.append(
        finding(
            "ULIQE.COMP.002",
            "completeness",
            FindingSeverity.WARNING,
            "Lesson summary field is not present on current ULI facade.",
            field_path="educational_structure.summary",
            recommendation="Add summary in a later ULI milestone; do not invent one in ULIQE.",
        )
    )

    for _key, path, label in _REQUIRED_SOFT:
        value = _get(path)
        if value in (None, "", []) or (isinstance(value, list) and not value):
            findings.append(
                finding(
                    "ULIQE.COMP.010",
                    "completeness",
                    FindingSeverity.ERROR,
                    f"Missing required educational element: {label}",
                    field_path=path,
                )
            )

    for _key, path, label in _OPTIONAL_INVENTORY:
        value = _get(path)
        if not nonempty_list(value):
            findings.append(
                finding(
                    "ULIQE.COMP.020",
                    "completeness",
                    FindingSeverity.WARNING,
                    f"Missing optional element: {label}",
                    field_path=path,
                    recommendation="Enrich ULI extractors in later milestones; ULIQE will not invent content.",
                )
            )

    if not nonempty_list(assess.get("assessment_opportunities")):
        findings.append(
            finding(
                "ULIQE.COMP.030",
                "completeness",
                FindingSeverity.WARNING,
                "No assessment opportunities detected on ULI.",
                field_path="assessment_structure.assessment_opportunities",
            )
        )

    if not (a11y.get("reading_level") or a11y.get("age_estimate")):
        findings.append(
            finding(
                "ULIQE.COMP.040",
                "completeness",
                FindingSeverity.ERROR,
                "Accessibility/readability metadata missing.",
                field_path="accessibility_structure",
            )
        )

    if not nonempty_list(obj.claim_ledger):
        findings.append(
            finding(
                "ULIQE.COMP.050",
                "completeness",
                FindingSeverity.CRITICAL,
                "Claim ledger is empty — no source-grounded semantic content.",
                field_path="claim_ledger",
            )
        )

    return findings
