"""Diagram / visual opportunity validation (titles, alt text gaps — report only)."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation._uli import coerce_uli, finding
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def validate_diagrams(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    resources = obj.learning_resources()
    visuals = list(resources.get("diagrams") or [])
    images = list(resources.get("images") or [])
    tables = list(resources.get("tables") or [])

    if not visuals and not images and not tables:
        findings.append(
            finding(
                "ULIQE.DIAG.001",
                "stem_accuracy",
                FindingSeverity.INFO,
                "No diagram/table/image resources detected on ULI.",
            )
        )
        return findings

    for i, row in enumerate(visuals):
        if not isinstance(row, dict):
            continue
        if not row.get("opportunity") and not row.get("title"):
            findings.append(
                finding(
                    "ULIQE.DIAG.010",
                    "stem_accuracy",
                    FindingSeverity.WARNING,
                    f"Visual opportunity[{i}] lacks title/caption text.",
                    field_path=f"learning_resources.diagrams[{i}]",
                )
            )
        if not row.get("alt_text") and not row.get("accessibility_description"):
            findings.append(
                finding(
                    "ULIQE.DIAG.011",
                    "accessibility",
                    FindingSeverity.WARNING,
                    f"Visual opportunity[{i}] lacks alt text / accessibility description.",
                    field_path=f"learning_resources.diagrams[{i}]",
                    recommendation="Require alt text when Visual Intelligence attaches assets.",
                )
            )
        if not (row.get("source_refs") or row.get("referenced_concept")):
            findings.append(
                finding(
                    "ULIQE.DIAG.012",
                    "semantic_integrity",
                    FindingSeverity.WARNING,
                    f"Visual opportunity[{i}] not linked to a source concept/refs.",
                    field_path=f"learning_resources.diagrams[{i}]",
                )
            )

    for i, block in enumerate(images):
        if isinstance(block, dict) and not block.get("text"):
            findings.append(
                finding(
                    "ULIQE.DIAG.020",
                    "accessibility",
                    FindingSeverity.WARNING,
                    f"Image block[{i}] has no OCR/alt text payload.",
                    field_path=f"learning_resources.images[{i}]",
                )
            )

    return findings
