"""Public service API for ULIQE — consume ULI only; never invent content."""

from __future__ import annotations

from typing import Any

from engines.universal_lesson_validation.validator import (
    certify_uli,
    compare_versions,
    generate_report,
    list_validation_rules,
    score_uli,
    validate_uli,
)

__all__ = [
    "validate_uli",
    "score_uli",
    "certify_uli",
    "generate_report",
    "compare_versions",
    "list_validation_rules",
    "gate_for_downstream",
]


def gate_for_downstream(uli: Any) -> dict[str, Any]:
    """
    Mandatory gate helper for future callers (AME/AIE/…/export/publication).

    Does not modify those engines. Callers should check ``allowed`` before
    automatic downstream flow. Gold/Silver/Needs Review require human review.
    """
    report = validate_uli(uli)
    return {
        "allowed": report.downstream_allowed,
        "certification": report.certification.value,
        "overall_score": report.overall_score,
        "report": report.to_dict(),
    }
