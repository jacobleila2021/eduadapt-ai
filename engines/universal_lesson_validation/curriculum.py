"""Curriculum validation — optional enrichment; never invents alignment."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation._uli import coerce_uli, finding
from engines.universal_lesson_validation.schemas import FindingSeverity, ValidationFinding


def validate_curriculum(uli: Any) -> list[ValidationFinding]:
    obj = coerce_uli(uli)
    findings: list[ValidationFinding] = []
    edu = obj.educational_structure()
    resolution = dict(edu.get("curriculum_resolution") or {})
    status = str(resolution.get("status") or "unknown")
    grounding = obj.grounding_mode

    if grounding == "uploaded_source" and status in {"unknown", "ambiguous"}:
        findings.append(
            finding(
                "ULIQE.CUR.001",
                "curriculum_accuracy",
                FindingSeverity.INFO,
                "Curriculum not recognized — valid for uploaded_source grounding (optional enrichment).",
                field_path="educational_structure.curriculum_resolution",
                evidence={"status": status},
            )
        )
    elif grounding == "official_curriculum_publish" and status in {"unknown", "ambiguous"}:
        findings.append(
            finding(
                "ULIQE.CUR.002",
                "curriculum_accuracy",
                FindingSeverity.ERROR,
                "Official curriculum publish requires recognized or user-declared curriculum.",
                field_path="educational_structure.curriculum_resolution",
                recommendation="Declare curriculum in user_metadata or enrich via UCF/CIE.",
            )
        )
    elif status in {"recognized", "user_declared"}:
        findings.append(
            finding(
                "ULIQE.CUR.003",
                "curriculum_accuracy",
                FindingSeverity.INFO,
                f"Curriculum resolution status={status}: {resolution.get('curriculum')}",
                evidence=resolution,
            )
        )

    findings.append(
        finding(
            "ULIQE.CUR.010",
            "curriculum_accuracy",
            FindingSeverity.WARNING,
            "Bloom's Taxonomy levels are not present on ULI (inventory gap).",
            field_path="learning_structure.bloom",
            recommendation="Populate via CIE/AME enrichment later; ULIQE will not invent Bloom tags.",
        )
    )
    findings.append(
        finding(
            "ULIQE.CUR.011",
            "curriculum_accuracy",
            FindingSeverity.WARNING,
            "Depth of Knowledge / prerequisite graph not present on ULI.",
            field_path="learning_structure.prerequisites",
            recommendation="Optional CIE graph match when curriculum is recognized.",
        )
    )

    if not obj.learning_structure().get("learning_objectives"):
        findings.append(
            finding(
                "ULIQE.CUR.020",
                "curriculum_accuracy",
                FindingSeverity.WARNING,
                "No learning objectives to map to curriculum outcomes.",
                field_path="learning_structure.learning_objectives",
            )
        )

    return findings
